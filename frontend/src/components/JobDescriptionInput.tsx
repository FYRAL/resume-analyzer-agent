import { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { PlayCircle, Briefcase } from 'lucide-react';

interface JobDescriptionInputProps {
  onAnalyze: (jobDescription: string, pdfFile: File | null) => void;
  pdfFile: File | null;
  className?: string;
}

export const JobDescriptionInput = ({ onAnalyze, pdfFile, className }: JobDescriptionInputProps) => {
  const [jobDescription, setJobDescription] = useState('');

  const handleAnalyze = () => {
    if (jobDescription.trim()) {
      onAnalyze(jobDescription, pdfFile);
    }
  };

  const isAnalyzeDisabled = !jobDescription.trim() || !pdfFile;

  return (
    <div className={className}>
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="job-description" className="text-base font-semibold flex items-center gap-2">
            <Briefcase className="h-4 w-4 text-primary" />
            Job Description
          </Label>
          <Textarea
            id="job-description"
            placeholder="Paste the job description here...

Include key requirements, responsibilities, and qualifications you're looking for in a candidate."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            className="min-h-[300px] resize-none bg-gradient-card border-border transition-smooth focus:border-primary focus:shadow-primary"
          />
        </div>
        
        <div className="space-y-3">
          <Button 
            onClick={handleAnalyze}
            disabled={isAnalyzeDisabled}
            variant="professional"
            size="lg"
            className="w-full"
          >
            <PlayCircle className="h-5 w-5" />
            Run Analysis
          </Button>
          
          {isAnalyzeDisabled && (
            <p className="text-sm text-muted-foreground text-center">
              {!pdfFile ? "Please upload a PDF resume first" : "Please enter a job description"}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};