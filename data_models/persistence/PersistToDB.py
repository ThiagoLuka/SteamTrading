
from data_models.persistence.BasePersistenceModel import BasePersistenceModel


class PersistToDB:

    @staticmethod
    def persist(data_type: str, data: list[dict], *args, **kwargs):
        data_persistence_object = BasePersistenceModel.model_names[data_type]
        data_persistence_object(data).save(*args, **kwargs)
