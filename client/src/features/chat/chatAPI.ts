import { Message } from "./chatSlice";

export async function sendMessage(messages: Message[]): Promise<Response> {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/v1/completion`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages }),
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    return response
}
