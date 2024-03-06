import { createSlice } from "@reduxjs/toolkit";

export interface Message {
    content: string
    role: "user" | "system" | "assistant"
}

export interface ChatState {
    messages: Message[];
    loading: boolean;
    error: string | null;
}

const initialState: ChatState = {
    messages: [],
    loading: false,
    error: null,
};

export const chatSlice = createSlice({
    name: "chat",
    initialState,
    reducers: {
        addMessage: (state, action) => {
            state.messages.push(action.payload);
        },
        updateLatestAssistantMessage: (state, action) => {
            const assistantMessages = state.messages.filter((message) => message.role === 'assistant');
            const latestAssistantMessage = assistantMessages[assistantMessages.length - 1];
            if (latestAssistantMessage) {
                latestAssistantMessage.content += action.payload;
            }
        }
    },
})

export const { addMessage, updateLatestAssistantMessage } = chatSlice.actions;
export default chatSlice.reducer;