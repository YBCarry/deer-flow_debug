'use client';

import { Upload, FileText, Clock, AlertCircle, CheckCircle } from 'lucide-react';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';

import { Alert, AlertDescription } from '~/components/ui/alert';
import { Badge } from '~/components/ui/badge';
import { Button } from '~/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '~/components/ui/card';
import { Label } from '~/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '~/components/ui/select';
import { Textarea } from '~/components/ui/textarea';

import type { Tab } from "./types";

interface PromptFileInfo {
  filename: string;
  size: number;
  last_modified: string;
  content_preview: string;
}

interface PromptListResponse {
  files: PromptFileInfo[];
  allowed_files: string[];
}

function PromptTabContent() {
  const [files, setFiles] = useState<PromptFileInfo[]>([]);
  const [allowedFiles, setAllowedFiles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [fileContent, setFileContent] = useState<string>('');
  const [uploadStatus, setUploadStatus] = useState<{type: 'success' | 'error' | null, message: string}>({
    type: null,
    message: ''
  });

  // Load prompt files list
  const loadFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch('https://equal-popular-slug.ngrok-free.app/api/prompts', {
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch files');
      }
      const data: PromptListResponse = await response.json();
      setFiles(data.files);
      setAllowedFiles(data.allowed_files);
    } catch (error) {
      console.error('Error loading files:', error);
      toast.error('Failed to load prompt files');
    } finally {
      setLoading(false);
    }
  };

  // Upload file
  const handleUpload = async () => {
    if (!selectedFile || !fileContent.trim()) {
      toast.error('Please select a file and provide content');
      return;
    }

    setUploading(true);
    try {
      const response = await fetch('https://equal-popular-slug.ngrok-free.app/api/prompts/upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          filename: selectedFile,
          content: fileContent
        })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail ?? 'Upload failed');
      }

      setUploadStatus({ type: 'success', message: result.message });
      toast.success(`Successfully uploaded ${selectedFile}`);
      setFileContent('');
      setSelectedFile('');
      await loadFiles(); // Refresh the files list
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setUploadStatus({ type: 'error', message: errorMessage });
      toast.error(`Upload failed: ${errorMessage}`);
    } finally {
      setUploading(false);
    }
  };

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  useEffect(() => {
    void loadFiles();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-medium">Prompt Templates</h3>
        <p className="text-sm text-muted-foreground">
          Manage system prompt files for different AI agents
        </p>
      </div>

      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Prompt File
          </CardTitle>
          <CardDescription>
            Upload or update prompt template files. Files are automatically backed up before replacement.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* File Selection */}
          <div className="space-y-2">
            <Label htmlFor="file-select">Select File</Label>
            <Select value={selectedFile} onValueChange={setSelectedFile}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a prompt file to upload" />
              </SelectTrigger>
              <SelectContent>
                {allowedFiles.map((filename) => (
                  <SelectItem key={filename} value={filename}>
                    {filename}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* File Content */}
          <div className="space-y-2">
            <Label htmlFor="content">File Content</Label>
            <Textarea
              id="content"
              placeholder="Paste or type your prompt content here..."
              value={fileContent}
              onChange={(e) => setFileContent(e.target.value)}
              className="min-h-[200px] font-mono text-sm"
            />
          </div>

          {/* Upload Status */}
          {uploadStatus.type && (
            <Alert variant={uploadStatus.type === 'error' ? 'destructive' : 'default'}>
              {uploadStatus.type === 'success' ? (
                <CheckCircle className="h-4 w-4" />
              ) : (
                <AlertCircle className="h-4 w-4" />
              )}
              <AlertDescription>{uploadStatus.message}</AlertDescription>
            </Alert>
          )}

          {/* Upload Button */}
          <Button 
            onClick={handleUpload} 
            disabled={uploading || !selectedFile || !fileContent.trim()}
            className="w-full"
          >
            {uploading ? 'Uploading...' : 'Upload File'}
          </Button>
        </CardContent>
      </Card>

      {/* Files List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Current Prompt Files
          </CardTitle>
          <CardDescription>
            Overview of all prompt template files in the system
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading files...</div>
          ) : (
            <div className="space-y-4">
              {files.map((file) => (
                <Card key={file.filename} className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium">{file.filename}</h4>
                        <Badge variant={file.size > 0 ? 'default' : 'secondary'}>
                          {file.size > 0 ? 'Available' : 'Not Found'}
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div className="flex items-center gap-4">
                          <span>Size: {formatFileSize(file.size)}</span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            Last modified: {formatDate(file.last_modified)}
                          </span>
                        </div>
                        {file.content_preview && (
                          <div className="mt-2">
                            <p className="text-xs bg-muted p-2 rounded italic">
                              {file.content_preview}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export const PromptTab: Tab = () => {
  return <PromptTabContent />;
};

PromptTab.displayName = "PromptTab";
PromptTab.icon = FileText;