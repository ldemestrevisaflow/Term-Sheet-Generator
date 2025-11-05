# Term Sheet Questionnaire to Template Population: Step-by-Step Guide

## Overview
This guide demonstrates how to create a process flow that collects data through an interactive HTML questionnaire and populates it into a Word document template (similar to your TSA/TFA generator pattern).

---

## PHASE 1: ARCHITECTURE PLANNING

### 1.1 Data Collection Strategy
**Define the data pipeline:**
- Questionnaire Form (HTML) → Form Validation → Data Object → Template Population → Word Document Generation

**Identify all template placeholders:**
```
[insert name and ABN of company]
[insert date]
[Non] Binding Term Sheet
[insert seller name]
[insert buyer name]
[insert purchase price]
[insert completion date]
[insert due diligence date]
[insert deposit amount]
[insert warranties text]
[insert non-compete period]
[insert suppliers list]
[insert customers list]
[insert signatories]
```

### 1.2 Data Mapping Architecture
Create a mapping between:
- **Form Field IDs** → **Data Object Properties** → **Template Placeholders**

Example:
```javascript
formMapping = {
  'companyName': { 
    templateField: '[insert name and ABN of company]',
    validation: 'required|text'
  },
  'purchasePrice': {
    templateField: '[insert purchase price]',
    validation: 'required|currency'
  }
}
```

### 1.3 Conditional Logic Architecture
**Identify conditional sections:**
- Binding vs Non-Binding sheet (mutually exclusive)
- Due diligence complexity (structured/unstructured)
- Management retention provisions
- Schedules (suppliers/customers if applicable)

---

## PHASE 2: HTML QUESTIONNAIRE ENHANCEMENT

### 2.1 Form Structure Organization
**Section 1: Core Transaction Details**
```html
<div class="form-group">
  <label class="form-label required">Company Name</label>
  <input type="text" id="companyName" class="form-control" 
         placeholder="Legal entity name" data-field="companyName">
</div>

<div class="form-group">
  <label class="form-label required">ABN</label>
  <input type="text" id="companyABN" class="form-control" 
         placeholder="XX XXX XXX XXX" data-field="companyABN">
</div>
```

### 2.2 Implement Data Validation Layer
```javascript
const validationRules = {
  companyName: {
    required: true,
    type: 'text',
    minLength: 2,
    maxLength: 200
  },
  purchasePrice: {
    required: true,
    type: 'currency',
    min: 0
  },
  termSheetDate: {
    required: true,
    type: 'date',
    format: 'd/m/Y'
  }
};

function validateForm() {
  const errors = [];
  for (let field in validationRules) {
    const value = document.getElementById(field).value;
    const rules = validationRules[field];
    
    if (rules.required && !value) {
      errors.push(`${field} is required`);
    }
    if (rules.type === 'currency' && isNaN(parseFloat(value))) {
      errors.push(`${field} must be a valid currency`);
    }
  }
  return errors;
}
```

### 2.3 Form State Management
```javascript
const formState = {
  // Core details
  termSheetDate: '',
  companyName: '',
  companyABN: '',
  sellerName: '',
  buyerName: '',
  
  // Transaction terms
  purchasePrice: '',
  depositAmount: '',
  completionDate: '',
  bindingStatus: 'non-binding', // binding OR non-binding
  
  // Conditions
  dueDiligenceDate: '',
  dueDiligenceType: 'structured', // structured OR unstructured
  conditionsPrecedent: '',
  
  // Warranties & Representations
  warrantiesIncluded: [],
  additionalWarranties: '',
  
  // Commercial terms
  nonCompetePeriod: 3,
  nonSolicitationPeriod: 12,
  exclusivityRequired: 'yes',
  exclusivityEndDate: '',
  liquidatedDamages: '',
  
  // Management
  retentionPersonnel: '',
  directorsResign: '',
  directorsNewAgreements: '',
  
  // Schedules
  suppliersSchedule: '',
  customersSchedule: '',
  
  // Legal
  jurisdiction: 'New South Wales',
  governingLaw: 'Australian Law',
  
  // Signatories
  buyerSignatories: '',
  sellerSignatories: ''
};
```

---

## PHASE 3: DATA SERIALIZATION & STORAGE

### 3.1 Implement LocalStorage for Draft Persistence
```javascript
function saveFormDraft() {
  const formData = captureFormState();
  localStorage.setItem('termSheetDraft', JSON.stringify(formData));
  showToast('Draft saved');
}

function loadFormDraft() {
  const saved = localStorage.getItem('termSheetDraft');
  if (saved) {
    const formData = JSON.parse(saved);
    populateFormFromData(formData);
  }
}

function captureFormState() {
  const state = {};
  document.querySelectorAll('[data-field]').forEach(field => {
    state[field.dataset.field] = field.value;
  });
  return state;
}

function populateFormFromData(data) {
  Object.keys(data).forEach(key => {
    const field = document.querySelector(`[data-field="${key}"]`);
    if (field) field.value = data[key];
  });
}
```

### 3.2 Export/Import Data JSON
```javascript
function exportFormAsJSON() {
  const data = captureFormState();
  const blob = new Blob([JSON.stringify(data, null, 2)], 
                        { type: 'application/json' });
  saveAs(blob, 'TermSheet_' + data.companyName + '_data.json');
}

function importFormFromJSON(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    const data = JSON.parse(e.target.result);
    populateFormFromData(data);
    showToast('Data imported successfully');
  };
  reader.readAsText(file);
}
```

---

## PHASE 4: WORD DOCUMENT TEMPLATE SETUP

### 4.1 Prepare Master Template for Placeholders
**In Word document, replace all static values with unique, findable placeholders:**

```
Original:   "Date: 1 November 2024"
Replace:    "Date: <<TERM_SHEET_DATE>>"

Original:   "Details: [insert name and ABN of company]"
Replace:    "Details: <<COMPANY_NAME_ABN>>"

Original:   "The Seller: [seller]"
Replace:    "The Seller: <<SELLER_NAME>>"

Original:   "The Buyer: [buyer]"
Replace:    "The Buyer: <<BUYER_NAME>>"
```

**Best Practice:** Use double angle brackets `<<PLACEHOLDER>>` to make them visually distinct and searchable.

### 4.2 Map Placeholders to Data Fields
```javascript
const placeholderMapping = {
  '<<TERM_SHEET_DATE>>': 'termSheetDate',
  '<<COMPANY_NAME_ABN>>': ['companyName', 'companyABN'],
  '<<SELLER_NAME>>': 'sellerName',
  '<<BUYER_NAME>>': 'buyerName',
  '<<PURCHASE_PRICE>>': 'purchasePrice',
  '<<COMPLETION_DATE>>': 'completionDate',
  '<<DUE_DILIGENCE_DATE>>': 'dueDiligenceDate',
  '<<DEPOSIT_AMOUNT>>': 'depositAmount',
  '<<NON_COMPETE_YEARS>>': 'nonCompetePeriod',
  '<<BINDING_STATUS>>': 'bindingStatus',
  '<<JURISDICTION>>': 'jurisdiction',
  '<<GOVERNING_LAW>>': 'governingLaw'
};
```

---

## PHASE 5: DOCUMENT GENERATION ENGINE

### 5.1 Install Required Dependencies
```bash
npm install docx
npm install file-saver
npm install mammoth  # For reading .docx files
```

### 5.2 Create Document Template Loader
```javascript
async function loadTemplateDocx(templatePath) {
  const response = await fetch(templatePath);
  const arrayBuffer = await response.arrayBuffer();
  
  // Convert to mammoth for text extraction
  const result = await mammoth.convertToHtml({ arrayBuffer });
  return result.value;
}

// Alternative: Use a pre-parsed template structure
const templateStructure = {
  title: 'TERM SHEET',
  sections: [
    {
      heading: 'BINDING STATUS',
      content: 'This is a <<BINDING_STATUS>> Term Sheet'
    },
    {
      heading: 'PARTIES',
      content: `
        Seller: <<SELLER_NAME>>
        Buyer: <<BUYER_NAME>>
        Company: <<COMPANY_NAME_ABN>>
      `
    }
  ]
};
```

### 5.3 Implement Placeholder Replacement Engine
```javascript
function replaceAllPlaceholders(text, data) {
  let result = text;
  
  for (let placeholder in placeholderMapping) {
    const dataKey = placeholderMapping[placeholder];
    
    if (Array.isArray(dataKey)) {
      // Multiple fields combined
      const combined = dataKey.map(k => data[k]).join(' - ');
      result = result.replaceAll(placeholder, combined);
    } else {
      // Single field
      result = result.replaceAll(placeholder, data[dataKey] || '');
    }
  }
  
  return result;
}

function formatCurrencyValue(value) {
  return new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD',
    minimumFractionDigits: 2
  }).format(value);
}
```

### 5.4 Build Conditional Content Generation
```javascript
function generateConditionalSections(data) {
  const sections = [];
  
  // BINDING STATUS section
  const bindingSection = new docx.Paragraph({
    text: data.bindingStatus === 'binding' 
      ? 'The parties agree that the mutual promises in this Term Sheet are binding upon each of them'
      : 'The parties agree that this Term Sheet reflects their proposed course of dealing only',
    spacing: { before: 200, after: 200 }
  });
  sections.push(bindingSection);
  
  // DUE DILIGENCE section
  if (data.dueDiligenceDate) {
    sections.push(
      new docx.Paragraph({
        text: 'DUE DILIGENCE',
        heading: docx.HeadingLevel.HEADING_2,
        spacing: { before: 200, after: 100 }
      }),
      new docx.Paragraph({
        text: `Due Diligence to be completed by: ${data.dueDiligenceDate}`,
        spacing: { after: 100 }
      }),
      new docx.Paragraph({
        text: `Type: ${data.dueDiligenceType}`,
        spacing: { after: 200 }
      })
    );
  }
  
  // MANAGEMENT RETENTION section
  if (data.retentionPersonnel) {
    sections.push(
      new docx.Paragraph({
        text: 'MANAGEMENT AND KEY PERSONNEL',
        heading: docx.HeadingLevel.HEADING_2,
        spacing: { before: 200, after: 100 }
      }),
      new docx.Paragraph({
        text: `Key Personnel Retention: ${data.retentionPersonnel}`,
        spacing: { after: 200 }
      })
    );
  }
  
  // EXCLUSIVITY section
  if (data.exclusivityRequired === 'yes') {
    sections.push(
      new docx.Paragraph({
        text: 'EXCLUSIVITY',
        heading: docx.HeadingLevel.HEADING_2,
        spacing: { before: 200, after: 100 }
      }),
      new docx.Paragraph({
        text: `Exclusivity Period Ends: ${data.exclusivityEndDate || 'As specified'}`,
        spacing: { after: 200 }
      })
    );
  }
  
  return sections;
}
```

### 5.5 Main Document Generation Function
```javascript
async function generateTermSheetDocument() {
  // Validate form
  const errors = validateForm();
  if (errors.length > 0) {
    showToast('Please fix: ' + errors.join(', '));
    return;
  }
  
  // Capture form data
  const data = captureFormState();
  
  // Build document children
  const children = [];
  
  // Title page
  children.push(
    new docx.Paragraph({
      text: 'TERM SHEET',
      heading: docx.HeadingLevel.HEADING_1,
      alignment: docx.AlignmentType.CENTER,
      spacing: { after: 200 }
    }),
    new docx.Paragraph({
      text: `Share Sale of ${data.companyName}`,
      alignment: docx.AlignmentType.CENTER,
      spacing: { after: 400 }
    })
  );
  
  // Details table
  const detailsTable = new docx.Table({
    rows: [
      new docx.TableRow({
        cells: [
          new docx.TableCell({ children: [new docx.Paragraph('Date')] }),
          new docx.TableCell({ children: [new docx.Paragraph(data.termSheetDate)] })
        ]
      }),
      new docx.TableRow({
        cells: [
          new docx.TableCell({ children: [new docx.Paragraph('Seller')] }),
          new docx.TableCell({ children: [new docx.Paragraph(data.sellerName)] })
        ]
      }),
      new docx.TableRow({
        cells: [
          new docx.TableCell({ children: [new docx.Paragraph('Buyer')] }),
          new docx.TableCell({ children: [new docx.Paragraph(data.buyerName)] })
        ]
      }),
      new docx.TableRow({
        cells: [
          new docx.TableCell({ children: [new docx.Paragraph('Company')] }),
          new docx.TableCell({ children: [new docx.Paragraph(`${data.companyName} (ABN: ${data.companyABN})`)] })
        ]
      })
    ]
  });
  children.push(detailsTable);
  
  // Key commercial terms
  children.push(
    new docx.Paragraph({
      text: 'PURCHASE PRICE AND KEY TERMS',
      heading: docx.HeadingLevel.HEADING_2,
      spacing: { before: 200, after: 100 }
    }),
    new docx.Paragraph({
      text: `Purchase Price: ${formatCurrencyValue(data.purchasePrice)}`,
      spacing: { after: 50 }
    }),
    new docx.Paragraph({
      text: `Deposit (if applicable): ${formatCurrencyValue(data.depositAmount)}`,
      spacing: { after: 50 }
    }),
    new docx.Paragraph({
      text: `Completion Date: ${data.completionDate}`,
      spacing: { after: 200 }
    })
  );
  
  // Add conditional sections
  const conditionalSections = generateConditionalSections(data);
  children.push(...conditionalSections);
  
  // Warranties section
  if (data.additionalWarranties) {
    children.push(
      new docx.Paragraph({
        text: 'WARRANTIES',
        heading: docx.HeadingLevel.HEADING_2,
        spacing: { before: 200, after: 100 }
      }),
      new docx.Paragraph({
        text: data.additionalWarranties,
        spacing: { after: 200 }
      })
    );
  }
  
  // Commercial terms
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
  
  // Schedules
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
        text: `Schedule 1 – Key Suppliers:\n${data.suppliersSchedule}`,
        spacing: { after: 100 }
      }));
    }
    
    if (data.customersSchedule) {
      children.push(new docx.Paragraph({
        text: `Schedule 2 – Key Customers:\n${data.customersSchedule}`,
        spacing: { after: 200 }
      }));
    }
  }
  
  // Legal framework
  children.push(
    new docx.Paragraph({
      text: 'LEGAL FRAMEWORK',
      heading: docx.HeadingLevel.HEADING_2,
      spacing: { before: 200, after: 100 }
    }),
    new docx.Paragraph({
      text: `Jurisdiction: ${data.jurisdiction}`,
      spacing: { after: 50 }
    }),
    new docx.Paragraph({
      text: `Governing Law: ${data.governingLaw}`,
      spacing: { after: 200 }
    })
  );
  
  // Signature block
  children.push(
    new docx.Paragraph({
      text: 'SIGNATURES',
      heading: docx.HeadingLevel.HEADING_2,
      spacing: { before: 200, after: 200 }
    }),
    new docx.Paragraph({
      text: 'Signed for and on behalf of the Seller:',
      spacing: { after: 100 }
    }),
    new docx.Paragraph({
      text: '_________________________\nSignature\n\n_________________________\nPrint Name',
      spacing: { after: 300 }
    }),
    new docx.Paragraph({
      text: 'Signed for and on behalf of the Buyer:',
      spacing: { after: 100 }
    }),
    new docx.Paragraph({
      text: '_________________________\nSignature\n\n_________________________\nPrint Name',
      spacing: { after: 200 }
    })
  );
  
  // Create and save document
  const doc = new docx.Document({
    sections: [{
      children: children
    }]
  });
  
  docx.Packer.toBlob(doc).then(blob => {
    saveAs(blob, `TermSheet_${data.companyName}_${data.termSheetDate.replace(/\//g, '-')}.docx`);
    showToast('Term Sheet generated successfully');
  });
}
```

---

## PHASE 6: IMPLEMENTATION CHECKLIST

### Front-End Enhancements
- [ ] Add all form fields with proper `data-field` attributes
- [ ] Implement validation rules for each field type
- [ ] Add conditional visibility logic for dependent fields
- [ ] Add save draft to localStorage
- [ ] Add export/import JSON functionality
- [ ] Add progress tracking
- [ ] Add sidebar navigation between sections

### Document Generation
- [ ] Install docx library
- [ ] Create placeholder mapping object
- [ ] Implement form data capture function
- [ ] Build conditional section generator
- [ ] Create main document generation function
- [ ] Test with various data combinations
- [ ] Verify formatting in generated documents

### Quality Assurance
- [ ] Validate all placeholders are replaced
- [ ] Test conditional logic paths
- [ ] Verify currency and date formatting
- [ ] Test with edge cases (empty optional fields, long text, etc.)
- [ ] Verify signature blocks render correctly
- [ ] Test schedule table generation

---

## PHASE 7: ADVANCED FEATURES

### 7.1 Template Library Management
```javascript
const templates = {
  'binding_full': { /* template structure */ },
  'non_binding_simple': { /* template structure */ },
  'binding_with_escrow': { /* template structure */ }
};

function selectTemplate(templateName) {
  const template = templates[templateName];
  populateFormFromTemplate(template);
}
```

### 7.2 Version Control & Audit Trail
```javascript
const auditLog = [];

function recordAudit(action, data, timestamp = new Date()) {
  auditLog.push({ action, data, timestamp });
  localStorage.setItem('termSheetAudit', JSON.stringify(auditLog));
}

function generateTermSheetWithAudit() {
  recordAudit('GENERATED', captureFormState());
  generateTermSheetDocument();
}
```

### 7.3 Data Validation Enhanced
```javascript
function validateBusinessRules(data) {
  const warnings = [];
  
  if (data.depositAmount > data.purchasePrice) {
    warnings.push('Warning: Deposit exceeds purchase price');
  }
  
  if (new Date(data.completionDate) < new Date(data.dueDiligenceDate)) {
    warnings.push('Error: Completion date before due diligence date');
  }
  
  if (data.nonCompetePeriod > 10) {
    warnings.push('Warning: Non-compete period unusually long');
  }
  
  return warnings;
}
```

---

## COMPARISON TO YOUR TSA/TFA GENERATOR

### Similarities
1. Form-based data collection with validation
2. Conditional logic (e.g., multiple paths based on user choice)
3. LocalStorage for draft persistence
4. Direct Word document generation using docx library
5. Progress tracking and multi-section layout

### Key Differences
| Aspect | TSA/TFA | Term Sheet |
|--------|---------|-----------|
| Document complexity | Moderate | High (conditional sections) |
| Template flexibility | Fixed structure | Multiple variants |
| Data dependencies | Linear | Tree-like conditionals |
| Schedule handling | Simple list | Complex tables |

---

## NEXT STEPS

1. **Extract your TSA/TFA generator code** from GitHub
2. **Identify reusable patterns** (form handling, validation, generation)
3. **Create a shared utility library** for both tools
4. **Build term sheet generator** using same patterns
5. **Consider creating a framework** for document generation

Would you like me to create a refactored version combining both tools?
