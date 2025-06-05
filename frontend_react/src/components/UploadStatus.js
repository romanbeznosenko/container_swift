import React, { useState, useEffect } from 'react';
import {
    Card, Badge, ProgressBar, Alert,
    ListGroup, Button, Spinner
} from 'react-bootstrap';
import { getUploadStatus } from '../services/uploadApiService';

const UploadStatus = ({ uploadId, refreshInterval = 3000, onComplete }) => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [pollingActive, setPollingActive] = useState(true);

    const fetchStatus = async () => {
        try {
            setError(null);
            const data = await getUploadStatus(uploadId);
            setStatus(data);

            if (data.status === 'completed' || data.status === 'failed') {
                setPollingActive(false);

                if (onComplete) {
                    onComplete(data);
                }
            }
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                err.message ||
                'Error fetching upload status'
            );
            setPollingActive(false);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();

        let intervalId = null;
        if (refreshInterval > 0) {
            intervalId = setInterval(() => {
                if (pollingActive) {
                    fetchStatus();
                }
            }, refreshInterval);
        }

        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }, [uploadId, refreshInterval, pollingActive]);

    const handleRefresh = () => {
        setLoading(true);
        fetchStatus();
    };


    const calculateProgress = () => {
        if (!status) return 0;

        if (status.status === 'pending') return 0;
        if (status.status === 'completed') return 100;
        if (status.status === 'failed') return 100;

        if (status.total_records === 0) return 50;

        const processed = status.processed + status.failed + status.skipped;
        return Math.floor((processed / status.total_records) * 100);
    };

    return (
        <Card className="mb-4">
            <Card.Header as="h5" className="d-flex justify-content-between align-items-center">
                Upload Status
                <Button
                    variant="outline-primary"
                    size="sm"
                    onClick={handleRefresh}
                    disabled={loading}
                >
                    {loading ? (
                        <Spinner
                            as="span"
                            animation="border"
                            size="sm"
                            role="status"
                            aria-hidden="true"
                        />
                    ) : (
                        'Refresh'
                    )}
                </Button>
            </Card.Header>
            <Card.Body>
                {loading && !status && (
                    <div className="text-center p-4">
                        <Spinner animation="border" role="status">
                            <span className="visually-hidden">Loading...</span>
                        </Spinner>
                        <p className="mt-2">Loading upload status...</p>
                    </div>
                )}

                {error && (
                    <Alert variant="danger">
                        {error}
                    </Alert>
                )}

                {status && (
                    <>
                        <ListGroup className="mb-3">
                            <ListGroup.Item>
                                <strong>Upload ID:</strong> <code>{status.id}</code>
                            </ListGroup.Item>
                            <ListGroup.Item>
                                <strong>File:</strong> {status.filename}
                            </ListGroup.Item>
                            <ListGroup.Item>
                                <strong>Status:</strong>{' '}
                                <Badge bg={
                                    status.status === 'pending' ? 'warning' :
                                        status.status === 'processing' ? 'info' :
                                            status.status === 'completed' ? 'success' :
                                                'danger'
                                }>
                                    {status.status.toUpperCase()}
                                </Badge>
                            </ListGroup.Item>
                            <ListGroup.Item>
                                <strong>Created:</strong>{' '}
                                {status.created_at ? new Date(status.created_at).toLocaleString() : 'N/A'}
                            </ListGroup.Item>
                        </ListGroup>

                        <div className="mb-3">
                            <div className="d-flex justify-content-between mb-1">
                                <span>Progress:</span>
                                <span>
                                    {status.processed} processed, {status.skipped} skipped, {status.failed} failed
                                    {status.total_records > 0 && ` (${status.total_records} total)`}
                                </span>
                            </div>
                            <ProgressBar>
                                <ProgressBar
                                    variant="success"
                                    now={status.total_records ? (status.processed / status.total_records) * 100 : 0}
                                    key={1}
                                />
                                <ProgressBar
                                    variant="warning"
                                    now={status.total_records ? (status.skipped / status.total_records) * 100 : 0}
                                    key={2}
                                />
                                <ProgressBar
                                    variant="danger"
                                    now={status.total_records ? (status.failed / status.total_records) * 100 : 0}
                                    key={3}
                                />
                            </ProgressBar>
                        </div>

                        <Alert
                            variant={
                                status.status === 'pending' ? 'warning' :
                                    status.status === 'processing' ? 'info' :
                                        status.status === 'completed' ? 'success' :
                                            'danger'
                            }
                        >
                            {status.message}
                        </Alert>

                        {status.error_details && status.error_details.length > 0 && (
                            <div className="mt-3">
                                <h6>Error Details:</h6>
                                <ListGroup variant="flush">
                                    {status.error_details.slice(0, 5).map((error, index) => (
                                        <ListGroup.Item key={index} className="text-danger">
                                            {error.swift_code ? `${error.swift_code}: ${error.error}` : error}
                                        </ListGroup.Item>
                                    ))}
                                    {status.error_details.length > 5 && (
                                        <ListGroup.Item className="text-muted">
                                            ...and {status.error_details.length - 5} more errors
                                        </ListGroup.Item>
                                    )}
                                </ListGroup>
                            </div>
                        )}

                        {pollingActive && (
                            <div className="text-muted mt-3 small">
                                <Spinner animation="border" size="sm" className="me-2" />
                                Auto-refreshing every {refreshInterval / 1000} seconds...
                            </div>
                        )}
                    </>
                )}
            </Card.Body>
        </Card>
    );
};

export default UploadStatus;