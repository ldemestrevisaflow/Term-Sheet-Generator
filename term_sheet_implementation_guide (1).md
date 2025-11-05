# Term Sheet Generator - Implementation Reference Guide

## Quick Start Checklist

```
STEP 1: Set Up Project Dependencies
[ ] npm install docx
[ ] npm install file-saver
[ ] npm install flatpickr (date picker)
[ ] Verify libraries loaded in HTML <script> tags

STEP 2: HTML Form Markup
[ ] Add all form sections with data-field attributes
[ ] Ensure unique field IDs
[ ] Add validation indicators (required *)
[ ] Implement date pickers

STEP 3: JavaScript Data Management
[ ] Create formState object structure
[ ] Implement captureFormState() function
[ ] Implement validation functions
[ ] Implement conditional logic handlers

STEP 4: Word Document Generation
[ ] Create placeholder mapping dictionary
[ ] Build document generation function
[ ] Implement conditional section builders
[ ] Test formatting and spacing

STEP 5: Testing & QA
[ ] Test all conditional paths
[ ] Verify placeholder replacement
[ ] Check document formatting
[ ] Test edge cases
```

---

## Code Snippets by Function

### 1. FORM STATE CAPTURE & MANAGEMENT

```javascript
// Define the form state object at global scope
const formState = {
  // Party Details
  termSheetDate: '',
  companyName: '',
  companyABN: '',
  sellerName: '',
  buyerName: '',
  sellerAddress: '',
  buyerAddress: '',
  
  // Transaction Structure
  shareStructure: '', // e.g., "100 fully paid ordinary shares"
  purchasePrice: '',
  depositAmount: '',
  depositTiming: '', // e.g., "on signing" or "on condition satisfaction"
  balancePayment: '', // e.g., "on completion"
  
  // Key Dates
  termSheetDate: '',
  signingDate: '',
  dueDiligenceDate: '',
  conditionSatisfactionDate: '',
  longFormDate: '',
  completionDate: '',
  
  // Binding Status & Conditions
  bindingStatus: 'non-binding', // 'binding' or 'non-binding'
  conditionsPrecedent: '',
  
  // Due Diligence
  dueDiligenceType: 'structured', // 'structured' or 'unstructured'
  dueDiligenceScope: '',
  
  // Warranties & Representations
  warrantyLength: '18', // months
  warrantyCarve: '', // carve-outs
  additionalWarranties: '',
  warrantiesIncluded: [], // array of warranty types
  
  // Commercial Terms
  nonCompetePeriod: '3', // years
  nonSolicitationPeriod: '12', // months
  nonSolicitationScope: '', // employees/customers
  exclusivityRequired: 'yes',
  exclusivityEndDate: '',
  liquidatedDamages: '',
  
  // Management & Personnel
  retentionPersonnel: '',
  retentionPeriod: '',
  retentionBonus: '',
  directorsResign: '',
  directorsNewAgreements: '',
  employeeConsents: '',
  
  // Financial Adjustments
  adjustmentsApply: 'yes',
  workingCapitalTarget: '',
  netDebtTarget: '',
  adjustmentMechanism: '', // e.g., "dollar for dollar"
  cappedAt: '',
  earnout: '',
  earnoutConditions: '',
  
  // Schedules & Schedules
  suppliersSchedule: '',
  customersSchedule: '',
  assetsSchedule: '',
  liabilitiesSchedule: '',
  
  // Legal Framework
  jurisdiction: 'New South Wales',
  governingLaw: 'Australian Law',
  disputeResolution: 'litigation', // or 'arbitration'
  arbitrationLocation: '',
  
  // Signatories
  buyerSignatories: '',
  sellerSignatories: '',
  buyerRepresentative: '',
  sellerRepresentative: ''
};

// Function: Capture current form state from DOM
function captureFormState() {
  const state = {};
  document.querySelectorAll('[data-field]').forEach(field => {
    const fieldName = field.dataset.field;
    
    if (field.type === 'checkbox') {
      state[fieldName] = field.checked;
    } else if (field.type === 'radio') {
      if (field.checked) state[fieldName] = field.value;
    } else if (field.tagName === 'SELECT') {
      state[fieldName] = field.value;
    } else {
      state[fieldName] = field.value;
    }
  });
  return state;
}

// Function: Populate form from data object
function populateFormFromData(data) {
  Object.keys(data).forEach(key => {
    const field = document.querySelector(`[data-field="${key}"]`);
    if (field) {
      if (field.type === 'checkbox') {
        field.checked = data[key];
      } else if (field.type === 'radio') {
        document.querySelector(`[data-field="${key}"][value="${data[key]}"]`).checked = true;
      } else {
        field.value = data[key];
      }
    }
  });
}

// Function: Save draft to localStorage
function saveDraft() {
  const draft = captureFormState();
  localStorage.setItem('termSheetDraft_' + new Date().getTime(), JSON.stringify(draft));
  const allDrafts = JSON.parse(localStorage.getItem('termSheetDrafts') || '[]');
  allDrafts.push({
    timestamp: new Date().toISOString(),
    company: draft.companyName,
    id: new Date().getTime()
  });
  localStorage.setItem('termSheetDrafts', JSON.stringify(allDrafts));
  showToast('Draft saved successfully');
}

// Function: Load draft from localStorage
function loadDraft(draftId) {
  const draft = localStorage.getItem('termSheetDraft_' + draftId);
  if (draft) {
    const data = JSON.parse(draft);
    populateFormFromData(data);
    showToast('Draft loaded');
  }
}
```

### 2. VALIDATION ENGINE

```javascript
// Validation rules configuration
const validationRules = {
  termSheetDate: {
    required: true,
    type: 'date',
    message: 'Term Sheet Date is required'
  },
  companyName: {
    required: true,
    type: 'text',
    minLength: 2,
    maxLength: 200,
    message: 'Company Name must be 2-200 characters'
  },
  companyABN: {
    required: true,
    type: 'abn',
    message: 'Valid ABN required (format: XX XXX XXX XXX)'
  },
  purchasePrice: {
    required: true,
    type: 'currency',
    min: 0,
    message: 'Purchase Price must be a valid positive number'
  },
  depositAmount: {
    required: false,
    type: 'currency',
    min: 0,
    message: 'Deposit must be a valid positive number'
  },
  completionDate: {
    required: true,
    type: 'date',
    message: 'Completion Date is required'
  },
  dueDiligenceDate: {
    required: false,
    type: 'date',
    message: 'Due Diligence Date must be a valid date'
  }
};

// Main validation function
function validateForm() {
  const errors = [];
  const warnings = [];
  const formData = captureFormState();
  
  // Check required fields
  Object.keys(validationRules).forEach(fieldName => {
    const rule = validationRules[fieldName];
    const value = formData[fieldName];
    
    if (rule.required && !value) {
      errors.push(`${rule.message}`);
      highlightField(fieldName, 'error');
    } else if (value) {
      const fieldError = validateField(fieldName, value, rule);
      if (fieldError) {
        errors.push(fieldError);
        highlightField(fieldName, 'error');
      } else {
        highlightField(fieldName, 'success');
      }
    }
  });
  
  // Business rule validation
  const businessWarnings = validateBusinessRules(formData);
  warnings.push(...businessWarnings);
  
  return { errors, warnings, isValid: errors.length === 0 };
}

// Field-level validation
function validateField(fieldName, value, rule) {
  switch (rule.type) {
    case 'abn':
      return validateABN(value) ? null : rule.message;
    
    case 'currency':
      if (isNaN(parseFloat(value)) || parseFloat(value) < (rule.min || 0)) {
        return rule.message;
      }
      return null;
    
    case 'date':
      return isValidDate(value) ? null : rule.message;
    
    case 'text':
      if (value.length < (rule.minLength || 0) || 
          value.length > (rule.maxLength || 999)) {
        return rule.message;
      }
      return null;
    
    default:
      return null;
  }
}

// Business rule validation
function validateBusinessRules(formData) {
  const warnings = [];
  
  // Check: Completion date after due diligence date
  if (formData.dueDiligenceDate && formData.completionDate) {
    const ddDate = new Date(formData.dueDiligenceDate);
    const complDate = new Date(formData.completionDate);
    if (complDate <= ddDate) {
      warnings.push('Warning: Completion date should be after due diligence date');
    }
  }
  
  // Check: Deposit less than purchase price
  if (formData.depositAmount && formData.purchasePrice) {
    if (parseFloat(formData.depositAmount) > parseFloat(formData.purchasePrice)) {
      warnings.push('Warning: Deposit exceeds purchase price');
    }
  }
  
  // Check: Non-compete period reasonable
  if (parseInt(formData.nonCompetePeriod) > 10) {
    warnings.push('Warning: Non-compete period of ' + formData.nonCompetePeriod + 
                  ' years is unusually long');
  }
  
  return warnings;
}

// Helper: Validate ABN format
function validateABN(abn) {
  // Remove spaces
  abn = abn.replace(/\s+/g, '');
  
  // Check format: 11 digits
  if (!/^\d{11}$/.test(abn)) return false;
  
  // Check ABN checksum (basic)
  const weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19];
  let sum = 0;
  
  for (let i = 0; i < 11; i++) {
    sum += parseInt(abn[i]) * weights[i];
  }
  
  return sum % 89 === 0;
}

// Helper: Validate date
function isValidDate(dateString) {
  const date = new Date(dateString);
  return date instanceof Date && !isNaN(date);
}

// Helper: Highlight field validation
function highlightField(fieldName, status) {
  const field = document.querySelector(`[data-field="${fieldName}"]`);
  if (!field) return;
  
  field.classList.remove('success', 'error');
  field.classList.add(status);
  
  if (status === 'error') {
    field.style.borderColor = '#c50f1f';
  } else if (status === 'success') {
    field.style.borderColor = '#107c10';
  }
}
```

### 3. CONDITIONAL LOGIC HANDLERS

```javascript
// Conditional visibility - show/hide sections based on input
function handleConditionals() {
  const formData = captureFormState();
  
  // Binding Status conditionals
  const bindingSection = document.getElementById('section-bindingStatement');
  if (bindingSection) {
    if (formData.bindingStatus === 'binding') {
      bindingSection.style.display = 'block';
      document.getElementById('bindingText').textContent = 
        'The parties agree that the mutual promises in this Term Sheet are binding...';
    } else {
      bindingSection.style.display = 'block';
      document.getElementById('bindingText').textContent = 
        'The parties agree that this Term Sheet reflects their proposed course of dealing only...';
    }
  }
  
  // Due Diligence conditionals
  const ddSection = document.getElementById('section-dueDiligence');
  if (ddSection) {
    ddSection.style.display = formData.dueDiligenceDate ? 'block' : 'none';
  }
  
  // Deposit conditionals
  const depositSection = document.getElementById('section-depositPayment');
  if (depositSection) {
    depositSection.style.display = formData.depositAmount ? 'block' : 'none';
  }
  
  // Exclusivity conditionals
  const exclusivitySection = document.getElementById('section-exclusivity');
  if (exclusivitySection) {
    exclusivitySection.style.display = formData.exclusivityRequired === 'yes' ? 'block' : 'none';
  }
  
  // Management retention conditionals
  const managementSection = document.getElementById('section-management');
  if (managementSection) {
    managementSection.style.display = formData.retentionPersonnel ? 'block' : 'none';
  }
  
  // Schedules conditionals
  const schedulesSection = document.getElementById('section-schedules');
  if (schedulesSection) {
    const hasSchedules = formData.suppliersSchedule || formData.customersSchedule;
    schedulesSection.style.display = hasSchedules ? 'block' : 'none';
  }
  
  // Earnout conditionals
  const earnoutSection = document.getElementById('section-earnout');
  if (earnoutSection) {
    earnoutSection.style.display = formData.earnout ? 'block' : 'none';
  }
}

// Add event listeners for real-time conditionals
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('[data-field]').forEach(field => {
    field.addEventListener('change', handleConditionals);
  });
});
```

### 4. DOCUMENT GENERATION ENGINE

```javascript
// Placeholder mapping configuration
const placeholderMapping = {
  // Party & Company Details
  '<<TERM_SHEET_DATE>>': 'termSheetDate',
  '<<SELLER_NAME>>': 'sellerName',
  '<<SELLER_ADDRESS>>': 'sellerAddress',
  '<<BUYER_NAME>>': 'buyerName',
  '<<BUYER_ADDRESS>>': 'buyerAddress',
  '<<COMPANY_NAME>>': 'companyName',
  '<<COMPANY_ABN>>': 'companyABN',
  '<<SHARE_STRUCTURE>>': 'shareStructure',
  
  // Financial Terms
  '<<PURCHASE_PRICE>>': 'purchasePrice',
  '<<DEPOSIT_AMOUNT>>': 'depositAmount',
  '<<COMPLETION_DATE>>': 'completionDate',
  
  // Conditions & Dates
  '<<DUE_DILIGENCE_DATE>>': 'dueDiligenceDate',
  '<<CONDITION_SATISFACTION_DATE>>': 'conditionSatisfactionDate',
  '<<CONDITIONS_PRECEDENT>>': 'conditionsPrecedent',
  
  // Warranties
  '<<WARRANTY_LENGTH>>': 'warrantyLength',
  '<<ADDITIONAL_WARRANTIES>>': 'additionalWarranties',
  
  // Commercial Terms
  '<<NON_COMPETE_PERIOD>>': 'nonCompetePeriod',
  '<<NON_SOLICITATION_PERIOD>>': 'nonSolicitationPeriod',
  '<<EXCLUSIVITY_END_DATE>>': 'exclusivityEndDate',
  '<<LIQUIDATED_DAMAGES>>': 'liquidatedDamages',
  
  // Management
  '<<RETENTION_PERSONNEL>>': 'retentionPersonnel',
  '<<RETENTION_BONUS>>': 'retentionBonus',
  '<<DIRECTORS_RESIGN>>': 'directorsResign',
  
  // Schedules
  '<<SUPPLIERS_SCHEDULE>>': 'suppliersSchedule',
  '<<CUSTOMERS_SCHEDULE>>': 'customersSchedule',
  
  // Legal
  '<<JURISDICTION>>': 'jurisdiction',
  '<<GOVERNING_LAW>>': 'governingLaw',
  
  // Signatories
  '<<SELLER_SIGNATORIES>>': 'sellerSignatories',
  '<<BUYER_SIGNATORIES>>': 'buyerSignatories'
};

// Formatting utility functions
function formatCurrency(value) {
  if (!value || isNaN(parseFloat(value))) return '';
  return new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
    minimumFractionDigits: 2
  }).format(parseFloat(value));
}

function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-AU').format(date);
}

function formatPercentage(value) {
  if (!value || isNaN(parseFloat(value))) return '';
  return parseFloat(value).toFixed(2) + '%';
}

// Build conditional sections for the document
function generateConditionalSections(data) {
  const sections = [];
  
  // 1. BINDING STATUS section
  if (data.bindingStatus) {
    sections.push({
      heading: 'BINDING STATUS',
      content: data.bindingStatus === 'binding' 
        ? 'The parties agree that the mutual promises in this Term Sheet are binding upon each of them, save for any terms specifically marked as non-binding.'
        : 'The parties agree that this Term Sheet reflects their proposed course of dealing only and, other than provisions relating to due diligence, exclusivity, non-compete, confidentiality and dispute resolution, no legally binding obligations will be created unless and until formal legal documents are executed.'
    });
  }
  
  // 2. DUE DILIGENCE section (only if date provided)
  if (data.dueDiligenceDate) {
    sections.push({
      heading: 'DUE DILIGENCE',
      items: [
        'The Buyer will conduct ' + (data.dueDiligenceType || 'appropriate') + ' due diligence investigations.',
        'Due diligence to be completed by: ' + formatDate(data.dueDiligenceDate),
        data.dueDiligenceScope ? 'Scope: ' + data.dueDiligenceScope : null
      ].filter(Boolean)
    });
  }
  
  // 3. DEPOSIT section (only if amount provided)
  if (data.depositAmount) {
    sections.push({
      heading: 'DEPOSIT AND PAYMENT TERMS',
      items: [
        'Deposit: ' + formatCurrency(data.depositAmount),
        'Deposit timing: ' + (data.depositTiming || 'To be determined'),
        'Balance payment on: ' + (data.balancePayment || 'Completion')
      ]
    });
  }
  
  // 4. EXCLUSIVITY section (only if required)
  if (data.exclusivityRequired === 'yes') {
    sections.push({
      heading: 'EXCLUSIVITY',
      items: [
        'The Seller agrees to deal exclusively with the Buyer.',
        data.exclusivityEndDate ? 'Exclusivity period ends: ' + formatDate(data.exclusivityEndDate) : null,
        data.liquidatedDamages ? 'Liquidated damages for breach: ' + formatCurrency(data.liquidatedDamages) : null
      ].filter(Boolean)
    });
  }
  
  // 5. MANAGEMENT & KEY PERSONNEL section
  if (data.retentionPersonnel || data.directorsResign) {
    sections.push({
      heading: 'MANAGEMENT AND KEY PERSONNEL',
      items: [
        data.retentionPersonnel ? 'Key Personnel Retention: ' + data.retentionPersonnel : null,
        data.retentionPeriod ? 'Retention Period: ' + data.retentionPeriod : null,
        data.retentionBonus ? 'Retention Bonus: ' + formatCurrency(data.retentionBonus) : null,
        data.directorsResign ? 'Directors to Resign: ' + data.directorsResign : null,
        data.directorsNewAgreements ? 'Directors Entering New Agreements: ' + data.directorsNewAgreements : null
      ].filter(Boolean)
    });
  }
  
  // 6. EARNOUT section (if applicable)
  if (data.earnout) {
    sections.push({
      heading: 'EARNOUT',
      items: [
        'The purchase price is subject to a potential earnout of: ' + formatCurrency(data.earnout),
        data.earnoutConditions ? 'Conditions: ' + data.earnoutConditions : null
      ].filter(Boolean)
    });
  }
  
  return sections;
}

// Main document generation function using docx library
async function generateTermSheetDocument() {
  try {
    // Validation
    const validation = validateForm();
    if (!validation.isValid) {
      showValidationErrors(validation.errors);
      return;
    }
    
    // Capture data
    const data = captureFormState();
    
    // Build document
    const children = [];
    
    // TITLE PAGE
    children.push(
      new docx.Paragraph({
        text: 'TERM SHEET',
        heading: docx.HeadingLevel.HEADING_1,
        alignment: docx.AlignmentType.CENTER,
        spacing: { before: 200, after: 100 },
        bold: true
      }),
      new docx.Paragraph({
        text: 'Share Sale Agreement',
        alignment: docx.AlignmentType.CENTER,
        spacing: { after: 200 },
        italics: true
      }),
      new docx.Paragraph({
        text: data.companyName || '[Company Name]',
        alignment: docx.AlignmentType.CENTER,
        spacing: { after: 400 },
        bold: true,
        size: 28
      })
    );
    
    // DETAILS TABLE
    const detailsTable = createDetailsTable(data);
    children.push(detailsTable);
    children.push(new docx.Paragraph({ text: '', spacing: { after: 200 } }));
    
    // TRANSACTION OVERVIEW
    children.push(
      new docx.Paragraph({
        text: 'TRANSACTION OVERVIEW',
        heading: docx.HeadingLevel.HEADING_2,
        spacing: { before: 200, after: 100 }
      }),
      new docx.Paragraph({
        text: `The Seller owns all issued shares (${data.shareStructure || 'the Shares'}) in ${data.companyName}.`,
        spacing: { after: 100 }
      }),
      new docx.Paragraph({
        text: `The Buyer has agreed to purchase the Shares from the Seller on the terms set out in this Term Sheet.`,
        spacing: { after: 200 }
      })
    );
    
    // PURCHASE PRICE
    children.push(
      new docx.Paragraph({
        text: 'PURCHASE PRICE',
        heading: docx.HeadingLevel.HEADING_2,
        spacing: { before: 200, after: 100 }
      }),
      new docx.Paragraph({
        text: `Purchase Price: ${formatCurrency(data.purchasePrice)}`,
        spacing: { after: 50 }
      })
    );
    
    if (data.depositAmount) {
      children.push(
        new docx.Paragraph({
          text: `Deposit: ${formatCurrency(data.depositAmount)}`,
          spacing: { after: 50 }
        })
      );
    }
    
    if (data.adjustmentsApply === 'yes') {
      children.push(
        new docx.Paragraph({
          text: 'Subject to adjustments as set out below.',
          spacing: { after: 200 }
        })
      );
    }
    
    // KEY DATES
    children.push(
      new docx.Paragraph({
        text: 'KEY DATES',
        heading: docx.HeadingLevel.HEADING_2,
        spacing: { before: 200, after: 100 }
      })
    );
    
    const datesTable = createDatesTable(data);
    children.push(datesTable);
    children.push(new docx.Paragraph({ text: '', spacing: { after: 200 } }));
    
    // COMMERCIAL TERMS
    children.push(
      new docx.Paragraph({
        text: 'COMMERCIAL TERMS',
        heading: docx.HeadingLevel.HEADING_2,
        spacing: { before: 200, after: 100 }
      }),
      new docx.Paragraph({
        text: `Non-Compete: ${data.nonCompetePeriod} years`,
        spacing: { after: 50 }
      }),
      new docx.Paragraph({
        text: `Non-Solicitation: ${data.nonSolicitationPeriod} months`,
        spacing: { after: 200 }
      })
    );
    
    // ADD CONDITIONAL SECTIONS
    const conditionalSections = generateConditionalSections(data);
    conditionalSections.forEach(section => {
      children.push(
        new docx.Paragraph({
          text: section.heading,
          heading: docx.HeadingLevel.HEADING_2,
          spacing: { before: 200, after: 100 }
        })
      );
      
      if (section.items) {
        section.items.forEach(item => {
          children.push(new docx.Paragraph({
            text: item,
            spacing: { after: 50 }
          }));
        });
      } else if (section.content) {
        children.push(new docx.Paragraph({
          text: section.content,
          spacing: { after: 200 }
        }));
      }
    });
    
    // SCHEDULES
    if (data.suppliersSchedule || data.customersSchedule) {
      children.push(
        new docx.Paragraph({
          text: 'SCHEDULES',
          heading: docx.HeadingLevel.HEADING_2,
          spacing: { before: 200, after: 100 }
        })
      );
      
      if (data.suppliersSchedule) {
        children.push(new docx.Paragraph({
          text: 'Schedule 1 – Key Suppliers',
          heading: docx.HeadingLevel.HEADING_3,
          spacing: { after: 50 }
        }));
        children.push(new docx.Paragraph({
          text: data.suppliersSchedule,
          spacing: { after: 100 }
        }));
      }
      
      if (data.customersSchedule) {
        children.push(new docx.Paragraph({
          text: 'Schedule 2 – Key Customers',
          heading: docx.HeadingLevel.HEADING_3,
          spacing: { after: 50 }
        }));
        children.push(new docx.Paragraph({
          text: data.customersSchedule,
          spacing: { after: 200 }
        }));
      }
    }
    
    // LEGAL FRAMEWORK
    children.push(
      new docx.Paragraph({
        text: 'LEGAL FRAMEWORK',
        heading: docx.HeadingLevel.HEADING_2,
        spacing: { before: 200, after: 100 }
      }),
      new docx.Paragraph({
        text: `Jurisdiction: ${data.jurisdiction || 'New South Wales'}`,
        spacing: { after: 50 }
      }),
      new docx.Paragraph({
        text: `Governing Law: ${data.governingLaw || 'Australian Law'}`,
        spacing: { after: 200 }
      })
    );
    
    // SIGNATURES
    children.push(
      new docx.Paragraph({
        text: 'SIGNATURES',
        heading: docx.HeadingLevel.HEADING_2,
        spacing: { before: 200, after: 200 }
      }),
      new docx.Paragraph({
        text: 'Signed for and on behalf of the Seller:',
        spacing: { after: 150 }
      }),
      new docx.Paragraph({
        text: '_________________________',
        spacing: { after: 30 }
      }),
      new docx.Paragraph({
        text: 'Signature',
        spacing: { after: 100 }
      }),
      new docx.Paragraph({
        text: '_________________________',
        spacing: { after: 30 }
      }),
      new docx.Paragraph({
        text: 'Print Name',
        spacing: { after: 300 }
      }),
      new docx.Paragraph({
        text: 'Signed for and on behalf of the Buyer:',
        spacing: { after: 150 }
      }),
      new docx.Paragraph({
        text: '_________________________',
        spacing: { after: 30 }
      }),
      new docx.Paragraph({
        text: 'Signature',
        spacing: { after: 100 }
      }),
      new docx.Paragraph({
        text: '_________________________',
        spacing: { after: 30 }
      }),
      new docx.Paragraph({
        text: 'Print Name',
        spacing: { after: 200 }
      })
    );
    
    // CREATE DOCUMENT
    const doc = new docx.Document({
      sections: [{
        children: children,
        properties: {
          page: {
            margin: {
              top: 1440, // 1 inch = 1440 twips
              right: 1440,
              bottom: 1440,
              left: 1440
            }
          }
        }
      }]
    });
    
    // SAVE DOCUMENT
    const filename = `TermSheet_${data.companyName}_${new Date().toISOString().split('T')[0]}.docx`;
    docx.Packer.toBlob(doc).then(blob => {
      saveAs(blob, filename);
      recordAudit('DOCUMENT_GENERATED', data);
      showToast('Term Sheet generated successfully');
    });
    
  } catch (error) {
    console.error('Document generation error:', error);
    showToast('Error generating document: ' + error.message);
  }
}

// Helper: Create details table
function createDetailsTable(data) {
  return new docx.Table({
    width: { size: 100, type: docx.WidthType.PERCENTAGE },
    rows: [
      createTableRow('Date', data.termSheetDate),
      createTableRow('Seller', data.sellerName),
      createTableRow('Buyer', data.buyerName),
      createTableRow('Company', data.companyName + (data.companyABN ? ' (ABN: ' + data.companyABN + ')' : '')),
      createTableRow('Purchase Price', formatCurrency(data.purchasePrice))
    ]
  });
}

// Helper: Create dates table
function createDatesTable(data) {
  const rows = [];
  if (data.signingDate) rows.push(createTableRow('Signing Date', formatDate(data.signingDate)));
  if (data.dueDiligenceDate) rows.push(createTableRow('DD Completion', formatDate(data.dueDiligenceDate)));
  if (data.completionDate) rows.push(createTableRow('Completion Date', formatDate(data.completionDate)));
  
  return new docx.Table({
    width: { size: 100, type: docx.WidthType.PERCENTAGE },
    rows: rows.length > 0 ? rows : [createTableRow('Date', 'To be agreed')]
  });
}

// Helper: Create table row
function createTableRow(label, value) {
  return new docx.TableRow({
    cells: [
      new docx.TableCell({
        children: [new docx.Paragraph(label)],
        shading: { fill: 'E8E8E8' }
      }),
      new docx.TableCell({
        children: [new docx.Paragraph(value || '')]
      })
    ]
  });
}

// Audit trail recording
function recordAudit(action, data) {
  const audit = {
    action: action,
    timestamp: new Date().toISOString(),
    company: data.companyName,
    user: 'Current User' // Could be enhanced with actual user tracking
  };
  
  let auditLog = JSON.parse(localStorage.getItem('termSheetAuditLog') || '[]');
  auditLog.push(audit);
  localStorage.setItem('termSheetAuditLog', JSON.stringify(auditLog));
}
```

### 5. EVENT HANDLERS & INITIALIZATION

```javascript
// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
  // Initialize date pickers
  flatpickr('#termSheetDate', {
    dateFormat: 'd/m/Y',
    minDate: 'today'
  });
  
  flatpickr('#dueDiligenceDate', {
    dateFormat: 'd/m/Y',
    minDate: 'today'
  });
  
  flatpickr('#completionDate', {
    dateFormat: 'd/m/Y',
    minDate: 'today'
  });
  
  // Initialize form handlers
  document.getElementById('generateBtn').addEventListener('click', generateTermSheetDocument);
  document.getElementById('clearBtn').addEventListener('click', clearForm);
  document.getElementById('saveDraftBtn').addEventListener('click', saveDraft);
  document.getElementById('exportBtn').addEventListener('click', exportFormAsJSON);
  
  // Add real-time conditional handling
  document.querySelectorAll('[data-field]').forEach(field => {
    field.addEventListener('change', () => {
      handleConditionals();
      updateProgress();
    });
  });
  
  // Load draft if exists
  const recentDraft = localStorage.getItem('termSheetDraft');
  if (recentDraft) {
    const response = confirm('Load previous draft?');
    if (response) {
      populateFormFromData(JSON.parse(recentDraft));
    }
  }
  
  // Initialize progress tracking
  updateProgress();
  handleConditionals();
});

// Clear form
function clearForm() {
  if (confirm('Are you sure you want to clear all data?')) {
    document.querySelectorAll('input, select, textarea').forEach(field => {
      if (field.type === 'checkbox' || field.type === 'radio') {
        field.checked = false;
      } else {
        field.value = '';
      }
    });
    handleConditionals();
    updateProgress();
    showToast('Form cleared');
  }
}

// Progress tracking
function updateProgress() {
  const total = document.querySelectorAll('[data-field]').length;
  const filled = Array.from(document.querySelectorAll('[data-field]')).filter(f => f.value).length;
  const percentage = Math.round((filled / total) * 100);
  
  const progressBar = document.querySelector('.progress-bar-fill');
  if (progressBar) {
    progressBar.style.width = percentage + '%';
  }
  
  const progressText = document.querySelector('.progress-text');
  if (progressText) {
    progressText.textContent = percentage + '% Complete';
  }
}

// Export form as JSON
function exportFormAsJSON() {
  const data = captureFormState();
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: 'application/json' });
  saveAs(blob, 'TermSheet_' + data.companyName + '_data.json');
  showToast('Data exported');
}

// Import form from JSON
function importFormFromJSON(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result);
      populateFormFromData(data);
      handleConditionals();
      updateProgress();
      showToast('Data imported successfully');
    } catch (error) {
      showToast('Error importing file: invalid JSON');
    }
  };
  reader.readAsText(file);
}

// Toast notifications
function showToast(message) {
  const toast = document.getElementById('toast');
  if (toast) {
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
  }
}

// Show validation errors
function showValidationErrors(errors) {
  const errorContainer = document.getElementById('validationErrors');
  if (errorContainer) {
    errorContainer.innerHTML = '<ul>' + errors.map(e => '<li>' + e + '</li>').join('') + '</ul>';
    errorContainer.style.display = 'block';
    errorContainer.scrollIntoView({ behavior: 'smooth' });
    setTimeout(() => {
      errorContainer.style.display = 'none';
    }, 5000);
  } else {
    showToast('Errors: ' + errors.join('; '));
  }
}
```

---

## Integration with Existing TSA/TFA Generator

Extract reusable utilities into a shared module:

```javascript
// shared-utils.js
const FormUtils = {
  captureFormState,
  populateFormFromData,
  saveDraft,
  loadDraft,
  validateForm,
  validateField,
  highlightField
};

const DocumentUtils = {
  formatCurrency,
  formatDate,
  formatPercentage,
  createDetailsTable,
  createTableRow
};

const UIUtils = {
  showToast,
  showValidationErrors,
  updateProgress,
  handleConditionals
};
```

Then import in both generators:

```html
<script src="shared-utils.js"></script>
<script src="term-sheet-generator.js"></script>
```

