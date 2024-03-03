import React from 'react';
import { Message } from '../features/chat/chatSlice';

interface MessageListProps {
  messages: Message[];
}

const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  return (
    <div className="flex flex-col overflow-y-auto items-center">
      {messages.map((message, index) => (
        <div key={index} className="p-2 w-full lg:w-1/2">
          <div className="flex items-center">
            <div className="px-2 py-1 rounded-full justify-center items-center flex" style={{ background: message.role === 'user' ? '#2F80ED' : '#9B2C2C' }}>
              <span className="text-xs select-none font-regular text-white">{message.role === 'user' ? 'U' : 'B'}</span>
            </div>
            <span className="ml-2 text-sm font-semibold text-white">{message.role === 'user' ? 'You' : 'Bot'}</span>
          </div>
          <span className="inline-block text-xs p-2 rounded text-white px-8 messageDisplay">
            {message.content.split('\n').map((line, index, array) => (
              <React.Fragment key={index}>
                {line}
                {index < array.length - 1 ? <br /> : null}
              </React.Fragment>
            ))}
          </span>
        </div>
      ))}
    </div>
  );
};

export default MessageList;