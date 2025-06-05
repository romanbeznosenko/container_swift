import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Card, Button, Spinner, Alert, Badge, Row, Col } from 'react-bootstrap';
import { fetchSwiftCodeByCode, deleteSwiftCode } from '../services/apiService';

const DetailPage = () => {
  const { swiftCode } = useParams();
  const navigate = useNavigate();
  
  const [swiftCodeData, setSwiftCodeData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  useEffect(() => {
    const loadSwiftCode = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchSwiftCodeByCode(swiftCode);
        setSwiftCodeData(data);
      } catch (err) {
        setError('Failed to load SWIFT code details. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (swiftCode) {
      loadSwiftCode();
    }
  }, [swiftCode]);

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete SWIFT code: ${swiftCode}?`)) {
      return;
    }

    try {
      setDeleteLoading(true);
      await deleteSwiftCode(swiftCode);
      navigate('/');
    } catch (err) {
      setError('Failed to delete SWIFT code. Please try again later.');
      console.error(err);
    } finally {
      setDeleteLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-spinner">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  if (!swiftCodeData) {
    return <Alert variant="warning">SWIFT code not found.</Alert>;
  }

  return (
    <div className="detail-container">
      <h1>SWIFT Code Details</h1>
      
      <Card className="my-4">
        <Card.Header as="h5" className="d-flex justify-content-between align-items-center">
          {swiftCodeData.swiftCode}
          {swiftCodeData.isHeadquarter && (
            <Badge bg="success">Headquarters</Badge>
          )}
        </Card.Header>
        
        <Card.Body>
          <Row className="mb-3">
            <Col sm={4} className="fw-bold">Country:</Col>
            <Col sm={8}>{swiftCodeData.countryName} ({swiftCodeData.countryISO2})</Col>
          </Row>
          
          <Row className="mb-3">
            <Col sm={4} className="fw-bold">Address:</Col>
            <Col sm={8}>{swiftCodeData.address}</Col>
          </Row>
          
          <Row className="mb-3">
            <Col sm={4} className="fw-bold">Headquarters Status:</Col>
            <Col sm={8}>{swiftCodeData.isHeadquarter ? 'Yes' : 'No'}</Col>
          </Row>
          
          <Row className="mb-3">
            <Col sm={4} className="fw-bold">SWIFT Code Format:</Col>
            <Col sm={8}>
              {swiftCodeData.swiftCode.length === 11 ? 
                '11 characters (includes branch code)' : 
                '8 characters (primary office)'}
            </Col>
          </Row>
          
          <div className="mt-4 d-flex justify-content-between">
            <Link to="/">
              <Button variant="secondary">Back to List</Button>
            </Link>
            <Button 
              variant="danger" 
              onClick={handleDelete}
              disabled={deleteLoading}
            >
              {deleteLoading ? (
                <>
                  <Spinner
                    as="span"
                    animation="border"
                    size="sm"
                    role="status"
                    aria-hidden="true"
                  />
                  <span className="ms-2">Deleting...</span>
                </>
              ) : (
                'Delete'
              )}
            </Button>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default DetailPage;