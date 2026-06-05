# apps/accounts/views.py

from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.views.generic import CreateView, TemplateView, UpdateView
from django.db import models
from django.http import HttpResponse, FileResponse, HttpResponseServerError
from django.utils.dateformat import format as datefmt

from .forms import SignUpForm, ProfileForm, CustomPasswordChangeForm
from .models import User
from apps.recipes.models import Recipe, RecipeIngredient
from apps.batches.models import Batch, BatchImage

import csv
import io
import json
import tempfile
import subprocess
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.serializers.json import DjangoJSONEncoder


class CustomLoginView(LoginView):
    template_name = "accounts/auth.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["login_form"] = ctx.get("form")
        ctx["signup_form"] = SignUpForm()
        return ctx

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_approved:
            messages.error(self.request, "Your account is pending admin approval.")
            return redirect("accounts:login")
        response = super().form_valid(form)
        self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        return response


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "accounts/auth.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["login_form"] = AuthenticationForm()
        ctx["signup_form"] = ctx.get("form")
        return ctx

    def form_valid(self, form):
        new_user = form.save()
        self._notify_admins(new_user)
        messages.info(
            self.request,
            "Account created! You'll be able to log in once an admin approves it."
        )
        return redirect("accounts:login")

    def _notify_admins(self, new_user):
        import logging
        from django.core.mail import send_mail
        logger = logging.getLogger(__name__)
        admin_emails = list(
            User.objects.filter(is_staff=True)
            .exclude(email='')
            .values_list('email', flat=True)
        )
        if not admin_emails:
            logger.warning("No admin emails configured — skipping pending-account notification.")
            return
        name = new_user.get_full_name() or new_user.username
        try:
            send_mail(
                subject="New Skål account pending approval",
                message=(
                    f"A new user has registered and is awaiting your approval.\n\n"
                    f"Username: {new_user.username}\n"
                    f"Name:     {name}\n"
                    f"Email:    {new_user.email or '(not provided)'}\n\n"
                    f"Review at /admin/accounts/user/?is_approved__exact=0\n\n"
                    f"Skål! 🍯"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
            )
        except Exception as exc:
            logger.error("Failed to send admin notification email: %s", exc)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        user_batches = Batch.objects.filter(user=user)
        active_batches = user_batches.filter(bottled_done=False).order_by('-primary_date')

        # Average ABV from batches that have both OG and FG
        completed = user_batches.filter(fg__isnull=False)
        avg_abv = None
        if completed.exists():
            total_abv = sum(
                (76.08 * (float(b.og) - float(b.fg)) / (1.775 - float(b.og)))
                * (float(b.fg) / 0.794)
                for b in completed
            )
            avg_abv = round(total_abv / completed.count(), 1)

        ctx['active_batches'] = active_batches
        ctx['total_batches'] = user_batches.count()
        ctx['active_count'] = active_batches.count()
        ctx['avg_abv'] = avg_abv
        ctx['total_recipes'] = Recipe.objects.filter(user=user).count()
        ctx['last_bottled'] = (
            user_batches.filter(bottled_done=True).order_by('-bottled_date').first()
        )
        ctx['recent_images'] = (
            BatchImage.objects.filter(batch__user=user)
            .select_related('batch')
            .order_by('-id')[:10]
        )
        # Legacy keys — still used by current home.html template
        ctx['newest_recipe'] = Recipe.objects.filter(
            models.Q(user=user) | models.Q(is_public=True) | models.Q(user__isnull=True)
        ).order_by('-pk').first()
        ctx['newest_batch'] = user_batches.order_by('-pk').first()

        if user.is_staff:
            ctx['pending_approvals'] = User.objects.filter(is_approved=False).count()

        return ctx


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")
    login_url = reverse_lazy("accounts:login")

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['password_form'] = CustomPasswordChangeForm(self.request.user)
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated.')
        return super().form_valid(form)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")
    login_url = reverse_lazy("accounts:login")


@login_required
@require_POST
def toggle_theme(request):
    user = request.user
    user.theme = 'dark' if user.theme == 'light' else 'light'
    user.save(update_fields=['theme'])
    next_url = request.POST.get('next', '/')
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = '/'
    return redirect(next_url)


@login_required
def export_user_data(request):
    if request.method != "POST":
        return render(request, "accounts/export_failed.html")

    export_format = request.POST.get("format")
    include_public = request.POST.get("include_public") == "on"
    user = request.user

    recipes = Recipe.objects.filter(user=user)
    batches = Batch.objects.filter(user=user)

    if include_public:
        recipes = recipes | Recipe.objects.filter(is_public=True).exclude(user=user)
        batches = batches | Batch.objects.filter(is_public=True).exclude(user=user)

    recipe_fields = [f.name for f in Recipe._meta.fields]
    batch_fields = [f.name for f in Batch._meta.fields]

    def get_ingredients_list(recipe):
        return [
            f"{ri.quantity.strip()} {ri.ingredient.name}".strip()
            for ri in RecipeIngredient.objects.filter(recipe=recipe).select_related("ingredient").order_by("order")
        ]

    def calculate_abv(og, fg):
        try:
            og = float(og)
            fg = float(fg)
            abv = (76.08 * (og - fg) / (1.775 - og)) * (fg / 0.794)
            return round(abv, 2)
        except (TypeError, ValueError, ZeroDivisionError):
            return None

    def estimate_calories(abv):
        try:
            return round(abv * 1.6 * 5)
        except (TypeError, ValueError):
            return None

    if export_format == "json":
        data = {
            "recipes": [
                {
                    **{
                        field: getattr(r, field).username if field == "user" and getattr(r, field) else getattr(r, field)
                        for field in recipe_fields
                    },
                    "ingredients": get_ingredients_list(r)
                } for r in recipes
            ],
            "batches": [
                {
                    **{
                        field: getattr(b, field).username if field == "user" and getattr(b, field) else
                               getattr(b.recipe, "name") if field == "recipe" and b.recipe else getattr(b, field)
                        for field in batch_fields
                    },
                    "abv": calculate_abv(b.og, b.fg),
                    "calories_per_glass": estimate_calories(calculate_abv(b.og, b.fg))
                } for b in batches
            ]
        }
        response = HttpResponse(json.dumps(data, indent=2, cls=DjangoJSONEncoder), content_type="application/json")
        response["Content-Disposition"] = "attachment; filename=export.json"
        return response

    elif export_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Recipes"])
        recipe_headers = recipe_fields + ["ingredients"]
        writer.writerow(recipe_headers)
        for r in recipes:
            row = [getattr(r, field) for field in recipe_fields]
            row.append("; ".join(get_ingredients_list(r)))
            writer.writerow(row)

        writer.writerow([])
        writer.writerow(["Batches"])
        batch_headers = batch_fields + ["abv", "calories_per_glass"]
        writer.writerow(batch_headers)
        for b in batches:
            row = [getattr(b, field) for field in batch_fields]
            abv = calculate_abv(b.og, b.fg)
            cal = estimate_calories(abv)
            row.extend([abv, cal])
            writer.writerow(row)

        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=export.csv"
        return response

    elif export_format == "txt":
        output = io.StringIO()

        output.write("Recipes:\n")
        for r in recipes:
            for field in recipe_fields:
                output.write(f"{field}: {getattr(r, field)}\n")
            ingredients = get_ingredients_list(r)
            output.write("Ingredients:\n")
            for ing in ingredients:
                output.write(f" - {ing}\n")
            output.write("\n")

        output.write("\nBatches:\n")
        for b in batches:
            for field in batch_fields:
                output.write(f"{field}: {getattr(b, field)}\n")
            abv = calculate_abv(b.og, b.fg)
            cal = estimate_calories(abv)
            if abv:
                output.write(f"ABV: {abv}%\n")
            if cal:
                output.write(f"Estimated Calories per Glass: {cal} cal (5oz)\n")
            output.write("\n")

        response = HttpResponse(output.getvalue(), content_type="text/plain")
        response["Content-Disposition"] = "attachment; filename=export.txt"
        return response

    elif export_format == "pdf":
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Body', fontSize=10, leading=13, alignment=TA_LEFT))
        flow = []

        flow.append(Paragraph("Recipes", styles["Heading1"]))

        for r in recipes.order_by("name"):
            flow.append(Paragraph(f"<b>{r.name}</b>", styles["Heading2"]))
            flow.append(Paragraph(f"Public: {'Yes' if r.is_public else 'No'}", styles["Body"]))
            flow.append(Paragraph(f"Batch Size: {r.batch_size} gallons", styles["Body"]))

            ingredients = get_ingredients_list(r)
            if ingredients:
                flow.append(Paragraph("Ingredients:", styles["Body"]))
                for ing in ingredients:
                    flow.append(Paragraph(f" - {ing}", styles["Body"]))

            flow.append(Paragraph("Instructions:", styles["Body"]))
            wrapped = r.instructions.replace("■", "<br/>")
            flow.append(Paragraph(wrapped, styles["Body"]))
            flow.append(Spacer(1, 12))

        flow.append(PageBreak())
        flow.append(Paragraph("Batches", styles["Heading1"]))

        for b in batches.order_by("name"):
            flow.append(Paragraph(f"<b>{b.name}</b>", styles["Heading2"]))
            flow.append(Paragraph(f"Public: {'Yes' if b.is_public else 'No'}", styles["Body"]))
            flow.append(Paragraph(f"Batch Size: {b.batch_size} gal", styles["Body"]))
            if b.recipe:
                flow.append(Paragraph(f"Linked Recipe: {b.recipe.name}", styles["Body"]))
            if b.og:
                flow.append(Paragraph(f"OG: {b.og}", styles["Body"]))
            if b.fg:
                flow.append(Paragraph(f"FG: {b.fg}", styles["Body"]))
            abv = calculate_abv(b.og, b.fg)
            if abv:
                flow.append(Paragraph(f"ABV: {abv}%", styles["Body"]))
            if b.primary_date:
                flow.append(Paragraph(f"Primary Date: {datefmt(b.primary_date, 'F j, Y')}", styles["Body"]))
            if b.secondary_date:
                flow.append(Paragraph(f"Secondary Date: {datefmt(b.secondary_date, 'F j, Y')}", styles["Body"]))
            if b.bottling_date:
                flow.append(Paragraph(f"Bottling Date: {datefmt(b.bottling_date, 'F j, Y')}", styles["Body"]))
            calories = estimate_calories(abv)
            if calories:
                flow.append(Paragraph(f"Estimated Calories per Glass: {calories} cal (5oz)", styles["Body"]))
            if b.notes:
                flow.append(Paragraph("Notes:", styles["Body"]))
                flow.append(Paragraph(b.notes.replace("■", "<br/>"), styles["Body"]))

            flow.append(Spacer(1, 12))

        doc.build(flow)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="export.pdf")

    elif export_format == "sql":
        db = settings.DATABASES["default"]
        engine = db.get("ENGINE")
        if "postgresql" not in engine:
            return HttpResponse("SQL export only supported for PostgreSQL.", status=400)

        db_name = db["NAME"]
        db_user = db.get("USER", "")
        db_host = db.get("HOST", "localhost")
        db_port = str(db.get("PORT", 5432))
        db_password = db.get("PASSWORD", "")

        try:
            env = {**os.environ, "PGPASSWORD": db_password}
            with tempfile.NamedTemporaryFile(suffix=".sql", delete=False) as tmp:
                subprocess.run(
                    ["pg_dump", "-U", db_user, "-h", db_host, "-p", db_port, "-d", db_name],
                    stdout=tmp,
                    stderr=subprocess.PIPE,
                    check=True,
                    env=env
                )
                tmp.flush()
                tmp.seek(0)
                buffer = open(tmp.name, "rb")
                return FileResponse(buffer, as_attachment=True, filename="database_dump.sql")
        except FileNotFoundError:
            return HttpResponseServerError("pg_dump not found. Is PostgreSQL client installed?")
        except subprocess.CalledProcessError as e:
            return HttpResponseServerError(f"pg_dump failed: {e.stderr.decode()}")

    return render(request, "accounts/export_failed.html")

