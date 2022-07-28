from service.bot_api_data_deserializers import (AssignDeserializerModel,
                                                CloseDeserializerModel,
                                                MessageFeedbackDeserializerModel)


ACTION_TO_DESERIALIZER = {
    "assign": AssignDeserializerModel,
    "close": CloseDeserializerModel,
    "message": MessageFeedbackDeserializerModel,
    "feedback": MessageFeedbackDeserializerModel,
}
