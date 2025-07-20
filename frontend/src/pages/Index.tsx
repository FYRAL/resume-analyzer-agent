import { useState } from 'react';
import { PdfUploader } from '@/components/PdfUploader';
import { JobDescriptionInput } from '@/components/JobDescriptionInput';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, Target } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const Index = () => {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [jobDesc, setJobDesc] = useState<string>('');
  const [analysis, setAnalysis] = useState<any>(null); 

  const { toast } = useToast();

  const handleAnalyze = async (jobDescription: string, file: File | null) => {
  if (!file || !jobDescription) {
    toast({ title: "Error", description: "Please upload a PDF and enter job description.",
      variant:"destructive",
     });
    return;
  }
 
  setJobDesc(jobDescription);
  toast({
    title: "Analysis Started",
    description: `Analyzing ${file.name}...`,
  });

  const form = new FormData();
  form.append("resume_pdf", file);
  form.append("job_desc", jobDescription);

  try {
    const res = await fetch("http://127.0.0.1:5000/api/analyze", {
      method: "POST",
      body: form,
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    setAnalysis(data); // store the result
   
  } catch (err) {
    console.error(err);
    toast({ title: "Error", description: "Analysis failed. Try again later." ,
       variant: "destructive",
    });
  }
};


  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header */}
      <div className="bg-background border-b border-border shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Job Scribe Analysis Hub
          </h1>
          <p className="text-muted-foreground">
            Upload a resume PDF and job description to get AI-powered insights.
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* PDF Uploader */}
          <Card className="bg-gradient-card shadow-lg border-border">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-foreground">
                <FileText className="h-5 w-5 text-primary" />
                Resume Upload
              </CardTitle>
            </CardHeader>
            <CardContent>
              <PdfUploader onFileSelect={setPdfFile} className="w-full" />
            </CardContent>
          </Card>

          {/* Job Description Input */}
          <Card className="bg-gradient-card shadow-lg border-border">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-foreground">
                <Target className="h-5 w-5 text-primary" />
                Job Description
              </CardTitle>
            </CardHeader>
            <CardContent>
              <JobDescriptionInput
                onAnalyze={(jd) => handleAnalyze(jd, pdfFile)}
                pdfFile={pdfFile}
                className="w-full"
              />
            </CardContent>
          </Card>
        </div>

        {/* 🎉 Analysis Result */}
        setAnalysis(data);

        // Then render it somewhere below:
        {analysis?.analysis_reasoning && (
           <div className="mt-8 p-4 bg-white rounded shadow">
           <h2 className="text-xl font-semibold">🧾 Analysis Summary</h2>
           <p className="whitespace-pre-line">{analysis.analysis_reasoning}</p>
        </div>
      )}  
      </div>
    </div>
  );
};

export default Index;
