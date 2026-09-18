"""Test suite for Task 4.5 — Interactive Developer Feedback & Few-Shot Prompt
Adaptation Engine.

This package marks ``tests/feedback`` as an importable package so pytest can
discover its modules without name collisions:

* ``test_models.py``      - FeedbackDecision / FeedbackRecord / FeedbackQuery /
                             RetrievedFeedback (pre-existing)
* ``test_store.py``       - FeedbackStore persistence (pre-existing)
* ``test_retriever.py``   - FeedbackRetriever scoring and filtering (pre-existing)
* ``test_adaptation.py``  - PromptAdaptationEngine / build_few_shot_context
* ``test_service.py``     - FeedbackService, the high-level public API

No fixtures, helpers or re-exports live here. Shared fixtures belong in a
``conftest.py`` if they're ever needed; nothing under
``agentshield.feedback`` is re-exported here because every test module
imports directly from ``agentshield.feedback.*``.
"""