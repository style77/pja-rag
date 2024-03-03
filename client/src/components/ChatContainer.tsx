import React from 'react';
import MessageList from './MessageList';
import SendMessageForm from './SendMessageForm';
import { useAppSelector } from '../app/hooks';
import { RootState } from '../app/store';

const ChatContainer = () => {
  const { messages } = useAppSelector((state: RootState) => state.chat);

  return (
    <div className="flex flex-col min-h-screen p-6 bg-zinc-900">
      <MessageList messages={messages} />
      <SendMessageForm />
    </div>
  );
};

export default ChatContainer;