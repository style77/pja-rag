import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { sendMessage } from "./chatAPI";

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

export const fetchCompletion = createAsyncThunk<
    { created_at: string; response: string },
    Message[],
    {
        rejectValue: string;
    }
>(import.meta.env.VITE_API_URL, async (messages, { rejectWithValue }) => {
    try {
        const response = await sendMessage(messages);
        return response.data;
    } catch (error: unknown) {
        if (error instanceof Error)
            return rejectWithValue(error.message);
        else
            return rejectWithValue('An unknown error occurred');
    }
});

export const chatSlice = createSlice({
    name: "chat",
    initialState,
    reducers: {
        addMessage: (state, action) => {
            state.messages.push(action.payload);
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchCompletion.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchCompletion.fulfilled, (state, action) => {
                state.loading = false;

                const responseMessage: Message = {
                    content: action.payload.response,
                    role: "assistant",
                }

                state.messages.push(responseMessage);
            })
            .addCase(fetchCompletion.rejected, (state, action) => {
                state.loading = false;
                state.error = typeof action.payload === 'string' ? action.payload : 'An unknown error occurred';
            });
    },
})

export const { addMessage } = chatSlice.actions;
export default chatSlice.reducer;