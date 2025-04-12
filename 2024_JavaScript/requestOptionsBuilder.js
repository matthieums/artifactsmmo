const token ="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Im1hcnRlbnMubWF0dGhpZXVAaG90bWFpbC5jb20iLCJwYXNzd29yZF9jaGFuZ2VkIjoiIn0.ARDWMe5_tUvMPvrrNR_-tuSAOcr1EWOPruhYFj3u_FY";

const defaultHeaders = new Headers();
defaultHeaders.append("Accept", "application/json");
defaultHeaders.append("Content-Type", "application/json");
defaultHeaders.append("Authorization", `Bearer ${token}`);


function buildGetRequestOptions() {
    const requestOptions = {
        method: 'GET',
        headers: new Headers(defaultHeaders),
        redirect: 'follow'
    };
    return requestOptions;
}

function buildPostRequestOptions(body) {
    const requestOptions = {
        method: 'POST',
        headers: new Headers(defaultHeaders),
        redirect: 'follow'
    }

    if (body) {
        requestOptions.body = JSON.stringify(body);
    }

    return requestOptions;
}

export default {
    buildGetRequestOptions,
    buildPostRequestOptions
}
