import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

from apps.batches.models import Batch
from apps.recipes.models import Recipe

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

    try:
        reply, input_tokens, output_tokens = call_ai(provider, api_key, system_prompt, history)
    except Exception as exc:
        logger.error("Bjorn AI call failed: %s", exc)
        reply = "Apologies, I couldn't reach the mead spirits just now. Try again in a moment."
        input_tokens = output_tokens = 0

    history.append({'role': 'assistant', 'content': reply})

    # Trim to last MAX_HISTORY messages
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    request.session[HISTORY_KEY] = history
    request.session.modified = True

    if input_tokens or output_tokens:
        AIUsage.objects.create(
            user=request.user,
            provider=provider,
            model=_model_name(provider),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

    return render(request, 'ai/partials/message.html', {'reply': reply})


def _model_name(provider):
    from .client import ANTHROPIC_MODEL, OPENAI_MODEL
    return ANTHROPIC_MODEL if provider == 'anthropic' else OPENAI_MODEL
