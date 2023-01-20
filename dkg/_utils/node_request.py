from dkg.types import NodeEndpoint


class NodeRequest:
    info = NodeEndpoint(method='get', path='info')
    bid_suggestion = NodeEndpoint(method='get', path='bid-suggestion')
    local_store = NodeEndpoint(method='post', path='local-store')
    publish = NodeEndpoint(method='post', path='publish')
    get = NodeEndpoint(method='post', path='get')
    query = NodeEndpoint(method='post', path='query')
