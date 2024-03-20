import React, { ChangeEvent, useState } from 'react';
import { addMessage, updateLatestAssistantMessage } from '../features/chat/chatSlice';
import { useAppDispatch, useAppSelector } from '../app/hooks';
import { RootState } from '../app/store';
import { Send } from 'lucide-react'

const SendMessageForm = () => {
  const [message, setMessage] = useState('');
  const dispatch = useAppDispatch();
  const { messages } = useAppSelector((state: RootState) => state.chat);

  const inputRef = React.useRef<HTMLTextAreaElement>(null);
  const formRef = React.useRef<HTMLFormElement>(null);

  const scrollToBottom = () => {
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: 'smooth',
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    const messagesCopy = [...messages];
    messagesCopy.push({ content: message, role: 'user' });

    setMessage('');

    dispatch(addMessage({ content: message, role: 'user' }));

    const response = await fetch(`${import.meta.env.VITE_API_URL}/v1/completion`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ messages: messagesCopy }),
    });

    if (!response.ok || response.status !== 200 || response.body === null) {
      throw new Error('Network response was not ok');
    }


    dispatch(addMessage({ content: "", role: 'assistant' }));

    const reader = response.body.getReader();

    let responding = true

    while (responding) {
      const { done, value } = await reader.read();

      if (done) {
        responding = false
        break;
      }

      const chunk = new TextDecoder().decode(value);
      const dataPieces = chunk.split('data:');

      for (const piece of dataPieces) {
        const formattedPiece = piece.trim();
        if (formattedPiece !== '') {
          const formattedChunk = ' ' + formattedPiece;
          dispatch(updateLatestAssistantMessage(formattedChunk));
          scrollToBottom();
        }
      }
    }

    inputRef.current?.focus();
    inputRef.current?.style.setProperty('height', '45px');
  };

  const handleInput = (e: ChangeEvent<HTMLTextAreaElement>) => {
    e.target.style.height = '45px';
    e.target.style.height = (e.target.scrollHeight) + "px";
  };

  return (
    <form className="mt-auto p-4 items-center justify-center flex" onSubmit={handleSubmit} ref={formRef}>
      <div className="relative flex items-center w-full lg:w-1/2">
        <textarea
          ref={inputRef}
          className="resize-none chat-input overflow-auto min-h-[45px] max-h-[50vh] border p-3.5 pr-10 w-full rounded-lg bg-transparent border-neutral-700 text-xs text-neutral-200 placeholder:text-neutral-600 font-regular focus:border focus:border-neutral-500 focus:outline-none"
          placeholder="Type a message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          style={{ maxHeight: '80vh', height: '45px' }}
          onInput={handleInput}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              formRef.current && formRef.current.requestSubmit()
            }
          }}
        />
        <button className="absolute right-3 bottom-3 text-neutral-200 disabled:text-neutral-600 transition duration-75" disabled={message.length < 1}>
          <Send size={20} />
        </button>
      </div>
    </form>
  );
};

export default SendMessageForm;
