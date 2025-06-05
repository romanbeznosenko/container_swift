import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Row, Col, Card, Alert } from 'react-bootstrap';
import FileUploader from '../components/FileUploader';
import UploadStatus from '../components/UploadStatus';

const UploadPage = () => {
    const navigate = useNavigate();
    const [uploadResult, setUploadResult] = useState(null);

    const handleUploadComplete = (result) => {
        setUploadResult(result);
    };

    const handleProcessingComplete = (result) => {
        console.log('Processing completed:', result);
    };

    return (
        <div>
            <h1 className="mb-4">Upload SWIFT Codes</h1>

            <Row>
                <Col lg={8}>
                    <FileUploader onUploadComplete={handleUploadComplete} />

                    <Card className="mb-4">
                        <Card.Header>
                            <h5>CSV File Template</h5>
                        </Card.Header>
                        <Card.Body>
                            <p>
                                Your CSV file should include the following columns:
                            </p>
                            <table className="table table-bordered table-striped">
                                <thead>
                                    <tr>
                                        <th>Column Name</th>
                                        <th>Description</th>
                                        <th>Example</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><code>SWIFT CODE</code></td>
                                        <td>The SWIFT/BIC code (8 or 11 characters)</td>
                                        <td>DEUTDEFF</td>
                                    </tr>
                                    <tr>
                                        <td><code>COUNTRY ISO2 CODE</code></td>
                                        <td>Two-letter ISO country code</td>
                                        <td>DE</td>
                                    </tr>
                                    <tr>
                                        <td><code>COUNTRY NAME</code></td>
                                        <td>Full name of the country</td>
                                        <td>Germany</td>
                                    </tr>
                                    <tr>
                                        <td><code>NAME</code></td>
                                        <td>Name of the bank/branch</td>
                                        <td>Deutsche Bank</td>
                                    </tr>
                                    <tr>
                                        <td><code>ADDRESS</code></td>
                                        <td>Physical address of the bank/branch</td>
                                        <td>Taunusanlage 12, 60325 Frankfurt am Main</td>
                                    </tr>
                                </tbody>
                            </table>

                            <Alert variant="info" className="mt-3">
                                <strong>Note:</strong> The system will automatically determine if a SWIFT code
                                represents a headquarters location based on whether it ends with 'XXX'.
                            </Alert>

                            <h6 className="mt-4">Example CSV Content:</h6>
                            <pre className="bg-light p-3 border rounded">
                                {`SWIFT CODE,COUNTRY ISO2 CODE,COUNTRY NAME,NAME,ADDRESS
DEUTDEFF,DE,Germany,Deutsche Bank,Taunusanlage 12 60325 Frankfurt am Main
DEUTDEFFXXX,DE,Germany,Deutsche Bank Headquarters,Taunusanlage 12 60325 Frankfurt am Main
CHASUS33,US,United States,JP Morgan Chase Bank,270 Park Avenue New York
CHASJPJT,JP,Japan,JP Morgan Chase Bank Tokyo,Tokyo Building 2-7-3 Marunouchi Chiyoda-ku`}
                            </pre>
                        </Card.Body>
                    </Card>
                </Col>

                <Col lg={4}>
                    {uploadResult && (
                        <UploadStatus
                            uploadId={uploadResult.id}
                            refreshInterval={3000}
                            onComplete={handleProcessingComplete}
                        />
                    )}

                    <Card>
                        <Card.Header>
                            <h5>Upload Tips</h5>
                        </Card.Header>
                        <Card.Body>
                            <ul className="ps-3">
                                <li>Make sure your CSV file has all the required columns</li>
                                <li>Ensure all SWIFT codes follow the correct format (8 or 11 characters)</li>
                                <li>SWIFT codes with "XXX" branch code are automatically marked as headquarters</li>
                                <li>Remove any duplicate SWIFT codes from your file before uploading</li>
                                <li>Files are processed in the background, so you can continue using the application</li>
                                <li>The upload service will handle your data even if you close the browser</li>
                            </ul>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default UploadPage;