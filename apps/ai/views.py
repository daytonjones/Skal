import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from apps.batches.models import Batch
from apps.recipes.models import Ingredient, Recipe, RecipeIngredient

from .client import call_ai
from .models import AIUsage

logger = logging.getLogger(__name__)

HISTORY_KEY = 'bjorn_history'
MAX_HISTORY = 10  # messages (user + assistant combined)


def _ai_enabled():
    return bool(getattr(settings, 'AI_PROVIDER', ''))


def _build_system_prompt(user):
    recipes = (
        Recipe.objects.filter(user=user)
        .prefetch_related('ingredients__ingredient')
        .order_by('-pk')[:10]
    )
    batches = Batch.objects.filter(user=user).order_by('-primary_date')[:10]

    recipe_lines = []
    for r in recipes:
        honeys = [
            ri.ingredient.name
            for ri in r.ingredients.all()
            if ri.ingredient.type == 'honey'
        ]
        yeasts = [
            ri.ingredient.name
            for ri in r.ingredients.all()
            if ri.ingredient.type == 'yeast'
        ]
        recipe_lines.append(
            f"- {r.name}: {r.volume_gallons} gal, "
            f"honey: {', '.join(honeys) or 'unspecified'}, "
            f"yeast: {', '.join(yeasts) or 'unspecified'}"
        )

    batch_lines = []
    for b in batches:
        gravity = f"OG {b.og}"
        if b.fg:
            gravity += f" → FG {b.fg}"
        batch_lines.append(f"- {b.name}: {b.stage}, {gravity}")

    recipes_text = '\n'.join(recipe_lines) if recipe_lines else 'No recipes yet.'
    batches_text = '\n'.join(batch_lines) if batch_lines else 'No batches yet.'

    return (
        "You are Bjorn, a friendly Viking mead-making expert and brewing assistant "
        "for Skål, a mead tracking app. You help with mead recipes, fermentation questions, "
        "ingredient suggestions, and troubleshooting. Be warm and knowledgeable — a Viking "
        "who loves sharing mead wisdom. Occasional Viking flavour is welcome but keep it "
        "natural, not forced.\n\n"
        "IMPORTANT: You ONLY answer questions related to mead making, homebrewing, "
        "fermentation, brewing ingredients, brewing equipment, and mead or brewing history. "
        "If asked about anything outside these topics — coding, general knowledge, writing, "
        "or any other unrelated subject — politely decline and redirect the user to mead "
        "topics. Do not assist with tasks outside your brewing expertise.\n\n"
        f"The user's recipes:\n{recipes_text}\n\n"
        f"The user's batches:\n{batches_text}\n\n"
        "When suggesting a new recipe, structure it with: name, batch size (gallons), "
        "honey type and amount (lbs), yeast strain, any additional ingredients, and brief "
        "notes — so the user can easily add it to Skål."
    )


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = 'ai/chat.html'

    def get(self, request, *args, **kwargs):
        if not _ai_enabled():
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['history'] = self.request.session.get(HISTORY_KEY, [])
        return ctx


@login_required
def send_message(request):
    if not _ai_enabled():
        raise Http404
    if request.method != 'POST':
        return HttpResponse(status=405)

    message = request.POST.get('message', '').strip()
    if not message:
        return HttpResponse(status=400)

    history = request.session.get(HISTORY_KEY, [])
    history.append({'role': 'user', 'content': message})

    provider = settings.AI_PROVIDER
    api_key = settings.AI_API_KEY
    system_prompt = _build_system_prompt(request.user)

    recipe_data = None
    try:
        reply, input_tokens, output_tokens, recipe_data = call_ai(
            provider, api_key, system_prompt, history
        )
    except Exception as exc:
        logger.error("Bjorn AI call failed: %s", exc)
        reply = "Apologies, I couldn't reach the mead spirits just now. Try again in a moment."
        input_tokens = output_tokens = 0

    history.append({'role': 'assistant', 'content': reply})

    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    request.session[HISTORY_KEY] = history

    if recipe_data:
        request.session['bjorn_pending_recipe'] = recipe_data
    else:
        request.session.pop('bjorn_pending_recipe', None)

    request.session.modified = True

    if input_tokens or output_tokens:
        AIUsage.objects.create(
            user=request.user,
            provider=provider,
            model=_model_name(provider),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    return render(request, 'ai/partials/message.html', {
        'reply': reply,
        'pending_recipe': recipe_data,
    })


@login_required
def save_recipe(request):
    if not _ai_enabled():
        raise Http404
    if request.method != 'POST':
        return HttpResponse(status=405)

    data = request.session.pop('bjorn_pending_recipe', None)
    request.session.modified = True

    if not data:
        messages.warning(request, "No pending recipe from Bjorn to save.")
        return redirect('ai:chat')

    try:
        recipe = Recipe.objects.create(
            user=request.user,
            name=data['name'],
            batch_size=data.get('batch_size', 5),
            instructions=data.get('instructions', ''),
        )

        order = 1
        honey_name = data.get('honey_name', '').strip()
        if honey_name:
            honey_ing = _get_or_create_ingredient(honey_name, Ingredient.TYPE_HONEY)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=honey_ing,
                quantity=data.get('honey_quantity', ''),
                order=order,
            )
            order += 1

        yeast_name = data.get('yeast', '').strip()
        if yeast_name:
            yeast_ing = _get_or_create_ingredient(yeast_name, Ingredient.TYPE_YEAST)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=yeast_ing,
                quantity='1 packet',
                order=order,
            )
            order += 1

        for extra in data.get('additional_ingredients', []):
            name = extra.get('name', '').strip()
            if not name:
                continue
            ing = _get_or_create_ingredient(name, Ingredient.TYPE_ADDITIVE)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ing,
                quantity=extra.get('quantity', ''),
                order=order,
            )
            order += 1

    except Exception as exc:
        logger.error("Failed to save Bjorn recipe: %s", exc)
        messages.error(request, "Something went wrong saving the recipe. Try again.")
        return redirect('ai:chat')

    messages.success(request, f'Recipe "{recipe.name}" saved! Review and edit it below.')
    return redirect('recipes:detail', pk=recipe.pk)


def _get_or_create_ingredient(name, ing_type):
    try:
        return Ingredient.objects.get(name__iexact=name)
    except Ingredient.DoesNotExist:
        return Ingredient.objects.create(name=name, type=ing_type)
    except Ingredient.MultipleObjectsReturned:
        return Ingredient.objects.filter(name__iexact=name).first()


def _model_name(provider):
    from .client import ANTHROPIC_MODEL, OPENAI_MODEL
    return ANTHROPIC_MODEL if provider == 'anthropic' else OPENAI_MODEL
