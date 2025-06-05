import React, { useState } from 'react';
import {
    Card, Form, Button, Alert, ProgressBar,
    Spinner, ListGroup, Badge
} from 'react-bootstrap';
import { uploadSwiftCodesFile } from '../services/uploadApiService';

const FileUploader = ({ onUploadComplete }) => {
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [uploadError, setUploadError] = useState(null);
    const [uploadResult, setUploadResult] = useState(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        setFile(selectedFile);
        setUploadError(null);
        setUploadResult(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!file) {
            setUploadError('Please select a file to upload');
            return;
        }

        if (!file.name.toLowerCase().endsWith('.csv')) {
            setUploadError('Only CSV files are allowed');
            return;
        }

        try {
            setIsUploading(true);
            setUploadProgress(0);
            setUploadError(null);
            setUploadResult(null);

            const progressInterval = setInterval(() => {
                setUploadProgress(prev => {
                    const newProgress = prev + 10;
                    return newProgress < 90 ? newProgress : prev;
                });
            }, 300);

            const result = await uploadSwiftCodesFile(file);

            clearInterval(progressInterval);
            setUploadProgress(100);

            setUploadResult(result);

            if (onUploadComplete) {
                onUploadComplete(result);
            }
        } catch (error) {
            setUploadError(
                error.response?.data?.detail ||
                error.message ||
                'Error uploading file'
            );
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <Card className="mb-4">
            <Card.Header as="h5">Upload SWIFT Codes</Card.Header>
            <Card.Body>
                <Card.Text>
                    Upload a CSV file containing SWIFT codes. The file should include columns for
                    SWIFT CODE, COUNTRY ISO2 CODE, COUNTRY NAME, NAME, and ADDRESS.
                </Card.Text>

                <Form onSubmit={handleSubmit}>
                    <Form.Group controlId="formFile" className="mb-3">
                        <Form.Label>Select CSV File</Form.Label>
                        <Form.Control
                            type="file"
                            onChange={handleFileChange}
                            accept=".csv"
                            disabled={isUploading}
                        />
                        <Form.Text className="text-muted">
                            Only CSV files are supported.
                        </Form.Text>
                    </Form.Group>

                    <Button
                        variant="primary"
                        type="submit"
                        disabled={!file || isUploading}
                    >
                        {isUploading ? (
                            <>
                                <Spinner
                                    as="span"
                                    animation="border"
                                    size="sm"
                                    role="status"
                                    aria-hidden="true"
                                    className="me-2"
                                />
                                Uploading...
                            </>
                        ) : (
                            'Upload File'
                        )}
                    </Button>
                </Form>

                {isUploading && (
                    <div className="mt-3">
                        <ProgressBar
                            now={uploadProgress}
                            label={`${uploadProgress}%`}
                            animated
                        />
                    </div>
                )}

                {uploadError && (
                    <Alert variant="danger" className="mt-3">
                        {uploadError}
                    </Alert>
                )}

                {uploadResult && (
                    <Alert variant="success" className="mt-3">
                        <Alert.Heading>File Uploaded Successfully!</Alert.Heading>
                        <p>
                            Your file has been uploaded and is now being processed.
                            You can check the status of your upload using the ID below.
                        </p>
                        <hr />
                        <ListGroup className="mb-3">
                            <ListGroup.Item>
                                <strong>Upload ID:</strong> <code>{uploadResult.id}</code>
                            </ListGroup.Item>
                            <ListGroup.Item>
                                <strong>File:</strong> {uploadResult.filename}
                            </ListGroup.Item>
                            <ListGroup.Item>
                                <strong>Status:</strong>{' '}
                                <Badge bg={
                                    uploadResult.status === 'pending' ? 'warning' :
                                        uploadResult.status === 'processing' ? 'info' :
                                            uploadResult.status === 'completed' ? 'success' :
                                                'danger'
                                }>
                                    {uploadResult.status.toUpperCase()}
                                </Badge>
                            </ListGroup.Item>
                            <ListGroup.Item>
                                <strong>Message:</strong> {uploadResult.message}
                            </ListGroup.Item>
                        </ListGroup>
                    </Alert>
                )}
            </Card.Body>
        </Card>
    );
};

export default FileUploader;