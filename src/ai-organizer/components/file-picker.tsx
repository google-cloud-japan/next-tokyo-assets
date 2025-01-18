'use client';

type FilePickerProps = {
  handleUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  label: string;
  accept: string;
  children: React.ReactNode;
  id: string;
};

const FilePicker = ({ handleUpload, children, label, accept, id }: FilePickerProps) => {
  return (
    <div className="h-[42px] min-h-[42px] pt-4">
      <label htmlFor={id} className="flex items-center">
        <input
          type="file"
          onChange={handleUpload}
          className="absolute left-[-9999px] opacity-0"
          id={id}
          accept={accept}
        />
        <div className="flex cursor-pointer items-center">
          {children}
          <p className="pl-4">{label}</p>
        </div>
      </label>
    </div>
  );
};

export default FilePicker;
