import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Card, Alert, Spinner } from 'react-bootstrap';
import { createSwiftCode } from '../services/apiService';

const CreatePage = () => {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        swiftCode: '',
        address: '',
        countryISO2: '',
        countryName: '',
        isHeadquarter: false
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [validationErrors, setValidationErrors] = useState({});

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData({
            ...formData,
            [name]: type === 'checkbox' ? checked : value
        });

        if (validationErrors[name]) {
            setValidationErrors({
                ...validationErrors,
                [name]: null
            });
        }
    };

    const handleSwiftCodeChange = (e) => {
        const swiftCode = e.target.value.toUpperCase();
        setFormData({
            ...formData,
            swiftCode,
            isHeadquarter: swiftCode.length === 11 && swiftCode.endsWith('XXX')
        });

        if (validationErrors.swiftCode) {
            setValidationErrors({
                ...validationErrors,
                swiftCode: null
            });
        }
    };

    const validateForm = () => {
        const errors = {};

        if (!formData.swiftCode) {
            errors.swiftCode = 'SWIFT code is required';
        } else if (![8, 11].includes(formData.swiftCode.length)) {
            errors.swiftCode = 'SWIFT code must be either 8 or 11 characters long';
        } else {
            const pattern = /^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$/;
            if (!pattern.test(formData.swiftCode)) {
                errors.swiftCode = 'Invalid SWIFT code format';
            }
        }

        if (formData.swiftCode.length === 11 && formData.swiftCode.endsWith('XXX') && !formData.isHeadquarter) {
            errors.isHeadquarter = 'SWIFT codes ending with XXX must be headquarters';
        } else if (formData.isHeadquarter && (!formData.swiftCode.endsWith('XXX') || formData.swiftCode.length !== 11)) {
            errors.isHeadquarter = 'Only SWIFT codes ending with XXX can be headquarters';
        }

        if (!formData.address) {
            errors.address = 'Address is required';
        }

        if (!formData.countryISO2) {
            errors.countryISO2 = 'Country code is required';
        } else if (formData.countryISO2.length !== 2) {
            errors.countryISO2 = 'Country code must be exactly 2 characters';
        } else if (!/^[A-Z]+$/.test(formData.countryISO2)) {
            errors.countryISO2 = 'Country code must contain only letters';
        }

        if (!formData.countryName) {
            errors.countryName = 'Country name is required';
        }

        return errors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        const errors = validateForm();
        if (Object.keys(errors).length > 0) {
            setValidationErrors(errors);
            return;
        }

        try {
            setLoading(true);
            setError(null);

            await createSwiftCode(formData);

            navigate('/');
        } catch (err) {
            if (err.response && err.response.data && err.response.data.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Failed to create SWIFT code. Please try again later.');
            }
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const countryOptions = [
        { code: 'US', name: 'United States' },
        { code: 'DE', name: 'Germany' },
        { code: 'GB', name: 'United Kingdom' },
        { code: 'JP', name: 'Japan' },
        { code: 'FR', name: 'France' },
        { code: 'CA', name: 'Canada' },
        { code: 'CN', name: 'China' },
        { code: 'AU', name: 'Australia' },
        { code: 'IT', name: 'Italy' },
        { code: 'ES', name: 'Spain' }
    ];

    const handleCountrySelect = (e) => {
        const countryCode = e.target.value;
        const country = countryOptions.find(c => c.code === countryCode);

        setFormData({
            ...formData,
            countryISO2: countryCode,
            countryName: country ? country.name : ''
        });

        // Clear validation errors
        if (validationErrors.countryISO2 || validationErrors.countryName) {
            setValidationErrors({
                ...validationErrors,
                countryISO2: null,
                countryName: null
            });
        }
    };

    return (
        <div className="form-container">
            <h1 className="mb-4">Add New SWIFT Code</h1>

            {error && <Alert variant="danger">{error}</Alert>}

            <Card>
                <Card.Body>
                    <Form onSubmit={handleSubmit}>
                        <Form.Group className="mb-3">
                            <Form.Label>SWIFT Code*</Form.Label>
                            <Form.Control
                                type="text"
                                name="swiftCode"
                                value={formData.swiftCode}
                                onChange={handleSwiftCodeChange}
                                placeholder="e.g., DEUTDEFF or DEUTDEFFXXX"
                                isInvalid={!!validationErrors.swiftCode}
                            />
                            <Form.Text className="text-muted">
                                8 characters (primary office) or 11 characters (specific branch)
                            </Form.Text>
                            <Form.Control.Feedback type="invalid">
                                {validationErrors.swiftCode}
                            </Form.Control.Feedback>
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>Country*</Form.Label>
                            <Form.Control
                                as="select"
                                name="countryISO2"
                                value={formData.countryISO2}
                                onChange={handleCountrySelect}
                                isInvalid={!!validationErrors.countryISO2 || !!validationErrors.countryName}
                            >
                                <option value="">Select a country</option>
                                {countryOptions.map(country => (
                                    <option key={country.code} value={country.code}>
                                        {country.name} ({country.code})
                                    </option>
                                ))}
                            </Form.Control>
                            <Form.Control.Feedback type="invalid">
                                {validationErrors.countryISO2 || validationErrors.countryName}
                            </Form.Control.Feedback>
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>Address*</Form.Label>
                            <Form.Control
                                type="text"
                                name="address"
                                value={formData.address}
                                onChange={handleChange}
                                placeholder="e.g., 123 Banking Street, City, Country"
                                isInvalid={!!validationErrors.address}
                            />
                            <Form.Control.Feedback type="invalid">
                                {validationErrors.address}
                            </Form.Control.Feedback>
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Check
                                type="checkbox"
                                label="This is a headquarters location"
                                name="isHeadquarter"
                                checked={formData.isHeadquarter}
                                onChange={handleChange}
                                isInvalid={!!validationErrors.isHeadquarter}
                                disabled={formData.swiftCode.length === 11 && formData.swiftCode.endsWith('XXX')}
                            />
                            <Form.Text className="text-muted">
                                SWIFT codes ending with XXX must be marked as headquarters.
                            </Form.Text>
                            <div className="invalid-feedback d-block">
                                {validationErrors.isHeadquarter}
                            </div>
                        </Form.Group>

                        <div className="d-flex justify-content-between">
                            <Button variant="secondary" onClick={() => navigate('/')}>
                                Cancel
                            </Button>
                            <Button
                                variant="primary"
                                type="submit"
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
                                        Creating...
                                    </>
                                ) : (
                                    'Create SWIFT Code'
                                )}
                            </Button>
                        </div>
                    </Form>
                </Card.Body>
            </Card>
        </div>
    );
};

export default CreatePage;