import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Row, Col, Card, Button, Form, 
  InputGroup, Pagination, Spinner, 
  Alert, Badge, Modal 
} from 'react-bootstrap';
import { fetchSwiftCodes, fetchSwiftCodesCount, deleteSwiftCode } from '../services/apiService';

const HomePage = () => {
  // State management
  const [swiftCodes, setSwiftCodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [itemsPerPage] = useState(10);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [countryFilter, setCountryFilter] = useState('');
  const [headquarterFilter, setHeadquarterFilter] = useState('');
  
  // Delete confirmation modal
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [codeToDelete, setCodeToDelete] = useState(null);

  // Fetch data on initial load and when filters change
  useEffect(() => {
    loadSwiftCodes();
  }, [currentPage, countryFilter, headquarterFilter]);

  const loadSwiftCodes = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const skip = (currentPage - 1) * itemsPerPage;
      
      // Convert headquarterFilter string to boolean or undefined
      let isHeadquarter;
      if (headquarterFilter === 'true') isHeadquarter = true;
      else if (headquarterFilter === 'false') isHeadquarter = false;
      
      // Try to fetch the total count
      try {
        const countResponse = await fetchSwiftCodesCount({
          country: countryFilter || undefined,
          isHeadquarter
        });
        
        setTotalCount(countResponse.count || 0);
      } catch (countError) {
        console.error('Error fetching count:', countError);
        // If count endpoint fails, we'll estimate based on current page
      }
      
      // Then fetch the actual data with pagination
      const data = await fetchSwiftCodes({
        skip,
        limit: itemsPerPage,
        country: countryFilter || undefined,
        isHeadquarter,
        search: searchTerm
      });
      
      console.log('API Response:', data);
      
      // If we have data but no total count, estimate a total
      if (Array.isArray(data) && data.length > 0 && totalCount === 0) {
        // If we have a full page, assume there's at least one more page
        if (data.length >= itemsPerPage) {
          setTotalCount((currentPage * itemsPerPage) + itemsPerPage);
        } else {
          // Otherwise, we're on the last page
          setTotalCount((currentPage - 1) * itemsPerPage + data.length);
        }
      }
      
      setSwiftCodes(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('API Error:', err);
      setError('Failed to load SWIFT codes. Please check that the API server is running and accessible. Error details: ' + (err.message || 'Unknown error'));
      setSwiftCodes([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle search form submission
  const handleSearch = (e) => {
    e.preventDefault();
    loadSwiftCodes();
  };

  // Handle filter changes
  const handleFilterChange = () => {
    setCurrentPage(1); // Reset to first page when filters change
    loadSwiftCodes();
  };

  // Handle delete confirmation
  const handleDeleteClick = (swiftCode) => {
    setCodeToDelete(swiftCode);
    setShowDeleteModal(true);
  };

  // Execute delete operation
  const handleConfirmDelete = async () => {
    if (!codeToDelete) return;
    
    try {
      await deleteSwiftCode(codeToDelete);
      setShowDeleteModal(false);
      loadSwiftCodes(); // Reload the list after deletion
    } catch (err) {
      setError('Failed to delete SWIFT code. Please try again later.');
      console.error(err);
    }
  };

  // Pagination controls
  const totalPages = Math.ceil(totalCount / itemsPerPage);
  
  const renderPagination = () => {
    // If there are too many pages, show a limited range
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    
    // Adjust the start if we're near the end
    if (endPage === totalPages) {
      startPage = Math.max(1, endPage - 4);
    }
    
    let items = [];
    
    // Always show first page
    if (startPage > 1) {
      items.push(
        <Pagination.Item 
          key={1} 
          active={1 === currentPage}
          onClick={() => setCurrentPage(1)}
        >
          1
        </Pagination.Item>
      );
      
      // Show ellipsis if there's a gap
      if (startPage > 2) {
        items.push(<Pagination.Ellipsis key="ellipsis1" disabled />);
      }
    }
    
    // Add the page range
    for (let number = startPage; number <= endPage; number++) {
      items.push(
        <Pagination.Item 
          key={number} 
          active={number === currentPage}
          onClick={() => setCurrentPage(number)}
        >
          {number}
        </Pagination.Item>
      );
    }
    
    // Always show last page
    if (endPage < totalPages) {
      // Show ellipsis if there's a gap
      if (endPage < totalPages - 1) {
        items.push(<Pagination.Ellipsis key="ellipsis2" disabled />);
      }
      
      items.push(
        <Pagination.Item 
          key={totalPages} 
          active={totalPages === currentPage}
          onClick={() => setCurrentPage(totalPages)}
        >
          {totalPages}
        </Pagination.Item>
      );
    }
    
    return (
      <Pagination>
        <Pagination.Prev 
          onClick={() => setCurrentPage(current => Math.max(current - 1, 1))}
          disabled={currentPage === 1}
        />
        {items}
        <Pagination.Next 
          onClick={() => setCurrentPage(current => Math.min(current + 1, totalPages))}
          disabled={currentPage === totalPages || totalPages === 0}
        />
      </Pagination>
    );
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>SWIFT Codes</h1>
        <Link to="/create">
          <Button variant="primary">+ Add New SWIFT Code</Button>
        </Link>
      </div>

      {/* Search Bar */}
      <Form onSubmit={handleSearch} className="search-bar">
        <InputGroup>
          <Form.Control
            placeholder="Search by SWIFT code, address or country..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <Button variant="outline-secondary" type="submit">
            Search
          </Button>
        </InputGroup>
      </Form>

      {/* Filters */}
      <div className="filters-section">
        <Row>
          <Col md={6}>
            <Form.Group>
              <Form.Label>Filter by Country</Form.Label>
              <Form.Control
                as="select"
                value={countryFilter}
                onChange={(e) => {
                  setCountryFilter(e.target.value);
                  handleFilterChange();
                }}
              >
                <option value="">All Countries</option>
                <option value="US">United States</option>
                <option value="DE">Germany</option>
                <option value="GB">United Kingdom</option>
                <option value="JP">Japan</option>
                <option value="FR">France</option>
                {/* Add more countries as needed */}
              </Form.Control>
            </Form.Group>
          </Col>
          <Col md={6}>
            <Form.Group>
              <Form.Label>Headquarters Status</Form.Label>
              <Form.Control
                as="select"
                value={headquarterFilter}
                onChange={(e) => {
                  setHeadquarterFilter(e.target.value);
                  handleFilterChange();
                }}
              >
                <option value="">All</option>
                <option value="true">Headquarters Only</option>
                <option value="false">Branches Only</option>
              </Form.Control>
            </Form.Group>
          </Col>
        </Row>
      </div>

      {/* Error Message */}
      {error && <Alert variant="danger">{error}</Alert>}


      {/* Loading Indicator */}
      {loading ? (
        <div className="loading-spinner">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
        </div>
      ) : (
        <>
          {/* SWIFT Codes List */}
          {swiftCodes.length === 0 ? (
            <Alert variant="info">No SWIFT codes found matching your criteria.</Alert>
          ) : (
            <Row>
              {swiftCodes.map((code) => (
                <Col md={6} lg={4} className="mb-4" key={code.swiftCode}>
                  <Card className="swift-code-card h-100">
                    <Card.Body>
                      <Card.Title>
                        {code.swiftCode}
                        {code.isHeadquarter && (
                          <Badge className="headquarters-badge">HQ</Badge>
                        )}
                      </Card.Title>
                      <Card.Subtitle className="mb-2 text-muted">
                        {code.countryName} ({code.countryISO2})
                      </Card.Subtitle>
                      <Card.Text>{code.address}</Card.Text>
                      <div className="d-flex justify-content-between">
                        <Link to={`/detail/${code.swiftCode}`}>
                          <Button variant="primary" size="sm">View Details</Button>
                        </Link>
                        <Button 
                          variant="danger" 
                          size="sm"
                          onClick={() => handleDeleteClick(code.swiftCode)}
                        >
                          Delete
                        </Button>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          )}

          {/* Pagination */}
          {totalCount > 0 && (
            <div className="mt-4">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <div>
                  Showing {Math.min(swiftCodes.length, 1) + (currentPage - 1) * itemsPerPage}-
                  {Math.min(currentPage * itemsPerPage, totalCount)} of {totalCount} SWIFT codes
                </div>
                {renderPagination()}
              </div>
            </div>
          )}
        </>
      )}

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Deletion</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Are you sure you want to delete the SWIFT code: <strong>{codeToDelete}</strong>?
          This action cannot be undone.
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleConfirmDelete}>
            Delete
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default HomePage;