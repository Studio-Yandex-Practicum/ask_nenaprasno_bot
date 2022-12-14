from starlette.routing import Route

from src import run_webhook_api

routes = [
    Route("/healthcheck", run_webhook_api.healthcheck_api, methods=["GET"]),
    Route("/bot/consultation/assign", run_webhook_api.consultation_assign, methods=["POST"]),
    Route("/bot/consultation/close", run_webhook_api.consultation_close, methods=["POST"]),
    Route("/bot/consultation/message", run_webhook_api.consultation_message, methods=["POST"]),
    Route("/bot/consultation/feedback", run_webhook_api.consultation_feedback, methods=["POST"]),
]
