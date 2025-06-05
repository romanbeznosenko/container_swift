import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Card, Button, Alert, Spinner } from 'react-bootstrap';
import UploadStatus from '../components/UploadStatus';

const UploadDetailPage = () => {
    const { uploadId } = useParams();
    const [loading, setLoading] = useState(true);


    useEffect(() => {
        const timer = setTimeout(() => {
            setLoading(false);
        }, 500);

        return () => clearTimeout(timer);
    }, []);

    if (loading) {
        return (
            <div className="text-center p-5">
                <Spinner animation="border" role="status">
                    <span className="visually-hidden">Loading...</span>
                </Spinner>
                <p className="mt-2">Loading upload details...</p>
            </div>
        );
    }

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>Upload Details</h1>
                <Link to="/uploads">
                    <Button variant="outline-secondary">
                        Back to Uploads
                    </Button>
                </Link>
            </div>

            {uploadId ? (
                <UploadStatus
                    uploadId={uploadId}
                    refreshInterval={5000}
                />
            ) : (
                <Alert variant="danger">
                    No upload ID provided.
                </Alert>
            )}

            <Card className="mt-4">
                <Card.Header>
                    <h5>About SWIFT Code Processing</h5>
                </Card.Header>
                <Card.Body>
                    <p>
                        When you upload a CSV file containing SWIFT codes, our system processes it in these steps:
                    </p>
                    <ol>
                        <li>Validate the CSV file format and required columns</li>
                        <li>Check each SWIFT code for valid format</li>
                        <li>Verify there are no duplicate SWIFT codes in the file</li>
                        <li>Process each record and send it to the main SWIFT code database</li>
                        <li>Handle any errors or duplicates found in the database</li>
                        <li>Provide a detailed report of the processing results</li>
                    </ol>
                    <p>
                        The upload service processes files asynchronously in the background,
                        so you can continue using the application while your file is being processed.
                    </p>
                    <p>
                        <strong>Required CSV columns:</strong>
                    </p>
                    <ul>
                        <li><code>SWIFT CODE</code>: The SWIFT/BIC code (8 or 11 characters)</li>
                        <li><code>COUNTRY ISO2 CODE</code>: The 2-letter ISO country code</li>
                        <li><code>COUNTRY NAME</code>: The full name of the country</li>
                        <li><code>NAME</code>: The name of the bank/branch</li>
                        <li><code>ADDRESS</code>: The physical address of the bank/branch</li>
                    </ul>
                </Card.Body>
            </Card>
        </div>
    );
};

export default UploadDetailPage;