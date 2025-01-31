from dkg.constants import (
    DefaultParameters,
    ZERO_ADDRESS,
    DEFAULT_PROXIMITY_SCORE_FUNCTIONS_PAIR_IDS,
)
from dkg.dataclasses import ParanetNodesAccessPolicy, ParanetMinersAccessPolicy


class InputService:
    def __init__(self, manager, config):
        self.manager = manager
        self.config = config

    def get_asset_get_arguments(self, options):
        return {
            "max_number_of_retries": self.get_max_number_of_retries(options),
            "frequency": self.get_frequency(options),
            "state": self.get_state(options),
            "include_metadata": self.get_include_metadata(options),
            "content_type": self.get_content_type(options),
            "validate": self.get_validate(options),
            "output_format": self.get_output_format(options),
            "hash_function_id": self.get_hash_function_id(options),
            "paranet_ual": self.get_paranet_ual(options),
            "subject_ual": self.get_subject_ual(options),
        }

    def get_asset_create_arguments(self, options):
        return {
            "max_number_of_retries": self.get_max_number_of_retries(options),
            "frequency": self.get_frequency(options),
            "epochs_num": self.get_epochs_num(options),
            "hash_function_id": self.get_hash_function_id(options),
            "score_function_id": self.get_score_function_id(options),
            "immutable": self.get_immutable(options),
            "token_amount": self.get_token_amount(options),
            "payer": self.get_payer(options),
            "minimum_number_of_finalization_confirmations": self.get_minimum_number_of_finalization_confirmations(
                options
            ),
            "minimum_number_of_node_replications": self.get_minimum_number_of_node_replications(
                options
            ),
        }

    def get_query_arguments(self, options):
        return {
            "max_number_of_retries": self.get_max_number_of_retries(options),
            "frequency": self.get_frequency(options),
            "paranet_ual": self.get_paranet_ual(options),
            "repository": self.get_repository(options),
        }

    def get_publish_finality_arguments(self, options):
        return {
            "max_number_of_retries": self.get_max_number_of_retries(options),
            "frequency": self.get_frequency(options),
            "minimum_number_of_finalization_confirmations": self.get_minimum_number_of_finalization_confirmations(
                options
            ),
        }

    def get_paranet_create_arguments(self, options):
        return {
            "paranet_name": self.get_paranet_name(options),
            "paranet_description": self.get_paranet_description(options),
            "paranet_nodes_access_policy": self.get_paranet_nodes_access_policy(
                options
            ),
            "paranet_miners_access_policy": self.get_paranet_miners_access_policy(
                options
            ),
        }

    def get_paranet_create_service_arguments(self, options):
        return {
            "paranet_service_name": self.get_paranet_service_name(options),
            "paranet_service_description": self.get_paranet_service_description(
                options
            ),
            "paranet_service_addresses": self.get_paranet_service_addresses(options),
        }

    def get_max_number_of_retries(self, options):
        return (
            options.get("max_number_of_retries")
            or self.config.get("max_number_of_retries")
            or DefaultParameters.MAX_NUMBER_OF_RETRIES.value
        )

    def get_frequency(self, options):
        return (
            options.get("frequency")
            or self.config.get("frequency")
            or DefaultParameters.FREQUENCY.value
        )

    def get_state(self, options):
        return (
            options.get("state")
            or self.config.get("state")
            or DefaultParameters.STATE.value
        )

    def get_include_metadata(self, options):
        return (
            options.get("include_metadata")
            or self.config.get("include_metadata")
            or DefaultParameters.INCLUDE_METADATA.value
        )

    def get_content_type(self, options):
        return (
            options.get("content_type")
            or self.config.get("content_type")
            or DefaultParameters.CONTENT_TYPE.value
        )

    def get_validate(self, options):
        return (
            options.get("validate")
            or self.config.get("validate")
            or DefaultParameters.VALIDATE.value
        )

    def get_output_format(self, options):
        return (
            options.get("output_format")
            or self.config.get("output_format")
            or DefaultParameters.OUTPUT_FORMAT.value
        )

    def get_hash_function_id(self, options):
        return (
            options.get("hash_function_id")
            or self.config.get("hash_function_id")
            or DefaultParameters.HASH_FUNCTION_ID.value
        )

    def get_paranet_ual(self, options):
        return (
            options.get("paranet_ual")
            or self.config.get("paranet_ual")
            or DefaultParameters.PARANET_UAL.value
        )

    def get_subject_ual(self, options):
        return (
            options.get("subject_ual")
            or self.config.get("subject_ual")
            or DefaultParameters.GET_SUBJECT_UAL.value
        )

    def get_epochs_num(self, options):
        return options.get("epochs_num") or self.config.get("epochs_num") or None

    def get_immutable(self, options):
        return (
            options.get("immutable")
            or self.config.get("immutable")
            or DefaultParameters.IMMUTABLE.value
        )

    def get_token_amount(self, options):
        return options.get("token_amount") or self.config.get("token_amount") or None

    def get_payer(self, options):
        return options.get("payer") or self.config.get("payer") or ZERO_ADDRESS

    def get_minimum_number_of_finalization_confirmations(self, options):
        return (
            options.get("minimum_number_of_finalization_confirmations")
            or self.config.get("minimum_number_of_finalization_confirmations")
            or DefaultParameters.MIN_NUMBER_OF_FINALIZATION_CONFIRMATION.value
            or None
        )

    def get_minimum_number_of_node_replications(self, options):
        return (
            options.get("minimum_number_of_node_replications")
            or self.config.get("minimum_number_of_node_replications")
            or None
        )

    def get_score_function_id(self, options):
        environment = (
            options.get("environment")
            or self.config.get("environment")
            or self.manager.blockchain_provider.environment
            or DefaultParameters.ENVIRONMENT.value
        )
        blockchain_name = (
            options.get("blockchain")
            or self.config.get("blockchain")
            or self.manager.blockchain_provider.blockchain_id
        )

        return DEFAULT_PROXIMITY_SCORE_FUNCTIONS_PAIR_IDS[environment][blockchain_name]

    def get_repository(self, options):
        return options.get("repository") or self.config.get("repository") or None

    def get_paranet_name(self, options):
        return options.get("paranet_name") or None

    def get_paranet_description(self, options):
        return options.get("paranet_description") or None

    def get_paranet_nodes_access_policy(self, options):
        return (
            options.get("paranet_nodes_access_policy") or ParanetNodesAccessPolicy.OPEN
        )

    def get_paranet_miners_access_policy(self, options):
        return (
            options.get("paranet_miners_access_policy")
            or ParanetMinersAccessPolicy.OPEN
        )

    def get_paranet_service_name(self, options):
        return options.get("paranet_service_name") or None

    def get_paranet_service_description(self, options):
        return options.get("paranet_service_description") or None

    def get_paranet_service_addresses(self, options):
        return options.get("paranet_service_addresses") or []
