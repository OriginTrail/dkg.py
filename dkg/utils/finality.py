from dkg.utils.node_request import NodeRequest
from dkg.method import Method
import time


_finality_status = Method(NodeRequest.finality_status)
_finality = Method(NodeRequest.finality)

def finality_status(
        ual: str,
        required_confirmations: int,
        max_number_of_retries: int,
        frequency: int,
    ):
        retries = 0
        finality = 0

        while finality < required_confirmations and retries <= max_number_of_retries:
            if retries > max_number_of_retries:
                raise Exception(
                    f"Unable to achieve required confirmations. "
                    f"Max number of retries ({max_number_of_retries}) reached."
                )

            # Sleep between attempts (except for first try)
            if retries > 0:
                time.sleep(frequency)
            
            retries += 1

            try:
                response = _finality_status(ual)
                finality = response.get("finality", 0)
                if finality >= required_confirmations:
                    break
            except Exception:
                finality = 0

        return finality

def finality(
        ual, 
        required_confirmations, 
        max_number_of_retries, 
        frequency
    ):
        finality_id = 0
        retries = 0

        while finality_id < required_confirmations and retries < max_number_of_retries:
            
            if retries > max_number_of_retries:
                raise Exception(
                    f"Unable to achieve required confirmations. "
                    f"Max number of retries ({max_number_of_retries}) reached."
                )

            if retries > 0:
                time.sleep(frequency)
            
            retries += 1

            try:
                response = _finality(ual) 
                operation_id = response.json().get("operationId", 0)
                if operation_id >= required_confirmations:
                    finality_id = operation_id 
                
            except Exception as e:
                finality_id = 0 
                print(f"Retry {retries + 1}/{max_number_of_retries} failed: {e}")
            
            return finality_id
