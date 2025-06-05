import React from 'react';
import { Link } from 'react-router-dom';
import { Alert, Button } from 'react-bootstrap';

const NotFoundPage = () => {
  return (
    <div className="text-center mt-5">
      <Alert variant="warning">
        <Alert.Heading>Page Not Found</Alert.Heading>
        <p>
          The page you are looking for does not exist or has been moved.
        </p>
      </Alert>
      <Link to="/">
        <Button variant="primary">Return to Home</Button>
      </Link>
    </div>
  );
};

export default NotFoundPage;