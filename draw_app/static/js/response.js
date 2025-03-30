'use strict';

const serverURL = 'https://ethical-mouse-diverse.ngrok-free.app';

async function makeResponse(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
    return await response.json();
}

export async function getResult(img, index) {
    const data = {
        img: img,
        index: index
    }

    try {
        let response = await makeResponse(serverURL, data);
        return response;
    } catch (error) {
        return {
            status: 'error',
            result: error
        }
    } 
}