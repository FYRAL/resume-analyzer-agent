import { useState, useRef } from 'react';
import { Upload, FileText, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface PdfUploaderProps {
  onFileSelect: (file: File | null) => void;
  className?: string;
}

export const PdfUploader = ({ onFileSelect, className }: PdfUploaderProps) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    const pdfFile = files.find(file => file.type === 'application/pdf');
    
    if (pdfFile) {
      setSelectedFile(pdfFile);
      onFileSelect(pdfFile);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      onFileSelect(file);
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    onFileSelect(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={cn("w-full", className)}>
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileSelect}
        className="hidden"
      />
      
      {selectedFile ? (
        <div className="bg-gradient-card border border-border rounded-lg p-6 shadow-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary/10 rounded-lg">
                <FileText className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="font-medium text-foreground">{selectedFile.name}</p>
                <p className="text-sm text-muted-foreground">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={removeFile}
              className="text-muted-foreground hover:text-destructive"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ) : (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={openFileDialog}
          className={cn(
            "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-smooth",
            "bg-gradient-subtle hover:bg-muted/50",
            isDragOver
              ? "border-primary bg-primary/5 shadow-primary"
              : "border-border"
          )}
        >
          <div className="flex flex-col items-center space-y-4">
            <div className={cn(
              "p-4 rounded-full transition-smooth",
              isDragOver ? "bg-primary/20" : "bg-muted"
            )}>
              <Upload className={cn(
                "h-8 w-8 transition-smooth",
                isDragOver ? "text-primary" : "text-muted-foreground"
              )} />
            </div>
            <div>
              <p className="text-lg font-medium text-foreground mb-2">
                Upload PDF Resume
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                Drag and drop your PDF file here, or click to browse
              </p>
              <Button variant="outline" size="sm">
                Choose File
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};