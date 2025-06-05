import React, { useState, useEffect } from 'react';
import {
    Row, Col, Card, Table, Badge, Button, Spinner,
    Pagination, Alert, Form, InputGroup
} from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { listUploads, getUploadStats } from '../services/uploadApiService';

const UploadsPage = () => {
    const [uploads, setUploads] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(10);

    const [statusFilter, setStatusFilter] = useState('');

    const [stats, setStats] = useState(null);
    const [statsLoading, setStatsLoading] = useState(true);

    const fetchUploads = async () => {
        try {
            setLoading(true);
            setError(null);

            const skip = (currentPage - 1) * itemsPerPage;

            const data = await listUploads({
                limit: itemsPerPage,
                skip,
                status: statusFilter || undefined
            });

            setUploads(data);
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                err.message ||
                'Error fetching uploads'
            );
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            setStatsLoading(true);
            const data = await getUploadStats();
            setStats(data);
        } catch (err) {
            console.error('Error fetching upload stats:', err);
        } finally {
            setStatsLoading(false);
        }
    };

    useEffect(() => {
        fetchUploads();
    }, [currentPage, statusFilter]);

    useEffect(() => {
        fetchStats();
    }, []);

    const handleFilterChange = (e) => {
        setStatusFilter(e.target.value);
        setCurrentPage(1);
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleString();
    };

    const getStatusBadge = (status) => {
        const variant =
            status === 'pending' ? 'warning' :
                status === 'processing' ? 'info' :
                    status === 'completed' ? 'success' :
                        'danger';

        return <Badge bg={variant}>{status.toUpperCase()}</Badge>;
    };

    const renderPagination = () => {
        return (
            <Pagination>
                <Pagination.Prev
                    onClick={() => setCurrentPage(current => Math.max(current - 1, 1))}
                    disabled={currentPage === 1 || loading}
                />
                <Pagination.Item active>{currentPage}</Pagination.Item>
                <Pagination.Next
                    onClick={() => setCurrentPage(current => current + 1)}
                    disabled={uploads.length < itemsPerPage || loading}
                />
            </Pagination>
        );
    };

    return (
        <div>
            <h1 className="mb-4">SWIFT Code Uploads</h1>

            <Row className="mb-4">
                <Col md={3}>
                    <Card className="text-center h-100">
                        <Card.Body>
                            <Card.Title>Total Uploads</Card.Title>
                            {statsLoading ? (
                                <Spinner animation="border" size="sm" />
                            ) : (
                                <h2>{stats?.total_uploads || 0}</h2>
                            )}
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={3}>
                    <Card className="text-center h-100 bg-success text-white">
                        <Card.Body>
                            <Card.Title>Successful</Card.Title>
                            {statsLoading ? (
                                <Spinner animation="border" size="sm" />
                            ) : (
                                <h2>{stats?.successful_uploads || 0}</h2>
                            )}
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={3}>
                    <Card className="text-center h-100 bg-danger text-white">
                        <Card.Body>
                            <Card.Title>Failed</Card.Title>
                            {statsLoading ? (
                                <Spinner animation="border" size="sm" />
                            ) : (
                                <h2>{stats?.failed_uploads || 0}</h2>
                            )}
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={3}>
                    <Card className="text-center h-100 bg-info text-white">
                        <Card.Body>
                            <Card.Title>Records Processed</Card.Title>
                            {statsLoading ? (
                                <Spinner animation="border" size="sm" />
                            ) : (
                                <h2>{stats?.records_processed || 0}</h2>
                            )}
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            <Card className="mb-4">
                <Card.Body>
                    <Row>
                        <Col md={6}>
                            <Form.Group>
                                <Form.Label>Filter by Status</Form.Label>
                                <Form.Select
                                    value={statusFilter}
                                    onChange={handleFilterChange}
                                >
                                    <option value="">All Statuses</option>
                                    <option value="pending">Pending</option>
                                    <option value="processing">Processing</option>
                                    <option value="completed">Completed</option>
                                    <option value="failed">Failed</option>
                                </Form.Select>
                            </Form.Group>
                        </Col>
                        <Col md={6} className="d-flex align-items-end">
                            <Button
                                variant="primary"
                                className="w-100"
                                onClick={() => {
                                    fetchUploads();
                                    fetchStats();
                                }}
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <Spinner
                                            as="span"
                                            animation="border"
                                            size="sm"
                                            role="status"
                                            aria-hidden="true"
                                            className="me-2"
                                        />
                                        Refreshing...
                                    </>
                                ) : (
                                    'Refresh Data'
                                )}
                            </Button>
                        </Col>
                    </Row>
                </Card.Body>
            </Card>

            {error && <Alert variant="danger">{error}</Alert>}

            <Card>
                <Card.Header>
                    <h4 className="mb-0">Upload History</h4>
                </Card.Header>
                <Card.Body>
                    {loading && uploads.length === 0 ? (
                        <div className="text-center p-4">
                            <Spinner animation="border" role="status">
                                <span className="visually-hidden">Loading...</span>
                            </Spinner>
                            <p className="mt-2">Loading uploads...</p>
                        </div>
                    ) : uploads.length === 0 ? (
                        <Alert variant="info">
                            No uploads found. Use the upload feature to add SWIFT codes.
                        </Alert>
                    ) : (
                        <Table responsive hover>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Filename</th>
                                    <th>Status</th>
                                    <th>Records</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {uploads.map(upload => (
                                    <tr key={upload.id}>
                                        <td>
                                            <code className="small">{upload.id.substring(0, 8)}...</code>
                                        </td>
                                        <td>{upload.filename}</td>
                                        <td>{getStatusBadge(upload.status)}</td>
                                        <td>
                                            {upload.processed} / {upload.total_records || '?'}
                                            {upload.failed > 0 && (
                                                <Badge bg="danger" className="ms-2">
                                                    {upload.failed} failed
                                                </Badge>
                                            )}
                                        </td>
                                        <td>{formatDate(upload.created_at)}</td>
                                        <td>
                                            <Link to={`/uploads/${upload.id}`}>
                                                <Button variant="outline-primary" size="sm">
                                                    Details
                                                </Button>
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    )}

                    <div className="d-flex justify-content-center mt-4">
                        {renderPagination()}
                    </div>
                </Card.Body>
            </Card>
        </div>
    );
};

export default UploadsPage;