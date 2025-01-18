type MessageUserProps = {
  content: string;
};

const MessageUser = ({ content }: MessageUserProps) => {
  return (
    <div className="flex w-full justify-end pb-5 pl-8">
      <div className="rounded-t-2xl rounded-bl-2xl bg-[#F7FBFF] p-5 text-sm shadow-md">{content}</div>
    </div>
  );
};

export default MessageUser;
