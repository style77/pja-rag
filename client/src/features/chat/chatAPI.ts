import { Message } from "./chatSlice";

export async function sendMessage(messages: Message[]): Promise<{
    data: {
        created_at: string;
        response: string;
    };
}> {
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

    const data: { created_at: string; response: string } = await response.json();
    return { data };
}
