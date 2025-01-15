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
            try:
                response = _finality_status(ual)
                finality = response.get("finality", 0)
                if finality >= required_confirmations:
                    break
            except Exception:
                finality = 0

            retries += 1

            if retries > max_number_of_retries:
                raise Exception(
                    f"Unable to achieve required confirmations. "
                    f"Max number of retries ({max_number_of_retries}) reached."
                )

            # Sleep between attempts (except for first try)
            if retries > 1:
                time.sleep(frequency)

        return finality

def finality(
        ual, 
        required_confirmations, 
        max_number_of_retries, 
        frequency
    ):
        finality = 0
        retries = 0

        while finality < required_confirmations and retries < max_number_of_retries:
            try:
                response = _finality(ual) 
                operation_id = response.json().get("operationId")
                return operation_id 
                
            except Exception as e:
                finality = 0 
                print(f"Retry {retries + 1}/{max_number_of_retries} failed: {e}")
            
            retries += 1
            time.sleep(frequency)  
        
        raise Exception(f"Finality not reached within {max_number_of_retries} retries.")
