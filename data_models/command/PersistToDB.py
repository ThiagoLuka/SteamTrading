
from data_models.command.BasePersistenceModel import BasePersistenceModel


class PersistToDB:

    @staticmethod
    def persist(data_type: str, data: list[dict], *args, **kwargs):
        data_persistence_object = BasePersistenceModel.models[data_type]
        data_persistence_object(data).save(*args, **kwargs)
