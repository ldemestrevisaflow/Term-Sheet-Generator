# Term Sheet Generator - Quick Reference Card

## One-Page Implementation Checklist

### Phase 1: HTML Form Structure (2 hours)
```html
<!-- Every input needs these attributes -->
<input type="text" 
       id="companyName"           <!-- Unique ID -->
       class="form-control"       <!-- Styling -->
       data-field="companyName"   <!-- Data mapping -->
       placeholder="Company name"
       required>                  <!-- Validation -->
```

**Checklist:**
- [ ] All inputs have `data-field` attribute
- [ ] All inputs have `id` attribute
- [ ] Required fields marked with `required` attribute
- [ ] Form sections have proper `id` for visibility control

---

### Phase 2: Form State Object (1 hour)
```javascript
const formState = {
  // Party Details
  termSheetDate: '',
  companyName: '',
  sellerName: '',
  buyerName: '',
  
  // Transaction
  purchasePrice: '',
  completionDate: '',
  
  // Conditions
  dueDiligenceDate: '',
  bindingStatus: 'non-binding',
  
  // Commercial
  nonCompetePeriod: '3',
  exclusivityRequired: 'yes'
};
```

**Key:** Every form field → object property

---

### Phase 3: Data Capture Functions (2 hours)

```javascript
// Capture form → object
function captureFormState() {
  const state = {};
  document.querySelectorAll('[data-field]').forEach(field => {
    state[field.dataset.field] = field.value;
  });
  return state;
}

// Object → form
function populateFormFromData(data) {
  Object.keys(data).forEach(key => {
    const field = document.querySelector(`[data-field="${key}"]`);
    if (field) field.value = data[key];
  });
}

// Save to localStorage
function saveDraft() {
  localStorage.setItem('draft', JSON.stringify(captureFormState()));
}
```

---

### Phase 4: Validation Rules (2 hours)

```javascript
const validationRules = {
  companyName: { required: true, minLength: 2, maxLength: 200 },
  purchasePrice: { required: true, type: 'currency', min: 0 },
  completionDate: { required: true, type: 'date' }
};

function validateForm() {
  const errors = [];
  const data = captureFormState();
  
  for (let field in validationRules) {
    const rule = validationRules[field];
    const value = data[field];
    
    if (rule.required && !value) {
      errors.push(`${field} is required`);
    }
  }
  
  return { isValid: errors.length === 0, errors };
}
```

---

### Phase 5: Conditional Sections (2 hours)

```javascript
function handleConditionals() {
  const data = captureFormState();
  
  // Show/hide based on values
  document.getElementById('section-exclusivity').style.display =
    data.exclusivityRequired === 'yes' ? 'block' : 'none';
    
  document.getElementById('section-duediligence').style.display =
    data.dueDiligenceDate ? 'block' : 'none';
}

// Trigger on every change
document.querySelectorAll('[data-field]').forEach(field => {
  field.addEventListener('change', handleConditionals);
});
```

---

### Phase 6: Placeholder Mapping (1 hour)

```javascript
const placeholders = {
  '<<SELLER_NAME>>': 'sellerName',
  '<<BUYER_NAME>>': 'buyerName',
  '<<COMPANY_NAME>>': 'companyName',
  '<<PURCHASE_PRICE>>': 'purchasePrice',
  '<<COMPLETION_DATE>>': 'completionDate',
  // ... all other placeholders
};
```

**In Word template, replace:**
```
[insert seller name] → <<SELLER_NAME>>
[insert buyer name]  → <<BUYER_NAME>>
$5,000,000           → <<PURCHASE_PRICE>>
31 January 2025      → <<COMPLETION_DATE>>
```

---

### Phase 7: Document Generation (4 hours)

```javascript
async function generateTermSheetDocument() {
  // 1. Validate
  const validation = validateForm();
  if (!validation.isValid) {
    showToast('Fix errors: ' + validation.errors.join(', '));
    return;
  }
  
  // 2. Capture data
  const data = captureFormState();
  
  // 3. Build document
  const children = [];
  
  children.push(
    new docx.Paragraph({
      text: 'TERM SHEET',
      heading: docx.HeadingLevel.HEADING_1,
      spacing: { after: 200 }
    }),
    new docx.Paragraph({
      text: `Share Sale of ${data.companyName}`,
      spacing: { after: 400 }
    })
  );
  
  // 4. Add sections (static and conditional)
  if (data.dueDiligenceDate) {
    children.push(
      new docx.Paragraph({
        text: 'DUE DILIGENCE',
        heading: docx.HeadingLevel.HEADING_2
      }),
      new docx.Paragraph({
        text: `Date: ${data.dueDiligenceDate}`
      })
    );
  }
  
  // 5. Create document
  const doc = new docx.Document({
    sections: [{ children }]
  });
  
  // 6. Save
  docx.Packer.toBlob(doc).then(blob => {
    saveAs(blob, `TermSheet_${data.companyName}.docx`);
    showToast('Generated successfully');
  });
}
```

---

## Function Call Order

```
User clicks "Generate"
    ↓
validateForm()           ← Catch errors
    ↓
captureFormState()       ← Get all data
    ↓
generateConditionalSections(data)  ← Build dynamic content
    ↓
Create docx.Document()   ← Build structure
    ↓
docx.Packer.toBlob()     ← Convert to file
    ↓
saveAs(blob, filename)   ← Download
    ↓
showToast('Success')     ← Notify user
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Form values don't save | Missing `data-field` attribute | Add `data-field="fieldName"` to every input |
| Placeholder not replaced | Typo in placeholder name | Check exact spelling in mapping object |
| Sections always show | Missing conditional logic | Add `handleConditionals()` call |
| Document generation fails | Validation passes but data missing | Check `captureFormState()` returns correct object |
| Downloaded file empty | docx library not loaded | Check `<script src="https://unpkg.com/docx...">` |

---

## Testing Checklist

```
□ All form fields capture correctly
  - Fill form → click Generate → check data object

□ Validation catches errors
  - Try empty required field → should error
  - Try invalid currency → should error
  - Try completion date before DD date → should warn

□ Conditionals work
  - Toggle exclusivity → section shows/hides
  - Add DD date → DD section appears
  - Remove DD date → DD section disappears

□ Document generates
  - All fields populate
  - No "<<PLACEHOLDER>>" text in output
  - Formatting is correct
  - Dates formatted as DD/MM/YYYY
  - Currency formatted with $ and decimals

□ Edge cases
  - Very long company name (200+ chars)
  - Special characters in text
  - Very large purchase price
  - All fields empty except required ones
```

---

## File Structure

```
/term-sheet-generator/
├── index.html                 ← Main form (enhance)
├── style.css                  ← Already has good styling
├── scripts/
│  ├── form-utils.js          ← NEW: data capture/validation
│  ├── document-generator.js  ← NEW: docx creation
│  └── main.js                ← NEW: event handlers
├── data/
│  └── term-sheet.docx        ← Master template (prep placeholders)
└── README.md                 ← This guide
```

---

## Libraries to Include

```html
<!-- In <head> -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css">

<!-- Before closing </body> -->
<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>
<script src="https://unpkg.com/docx@7.1.0/build/index.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/FileSaver.js/2.0.5/FileSaver.min.js"></script>

<!-- Your scripts -->
<script src="scripts/form-utils.js"></script>
<script src="scripts/document-generator.js"></script>
<script src="scripts/main.js"></script>
```

---

## Currency & Date Formatting

```javascript
function formatCurrency(value) {
  return new Intl.NumberFormat('en-AU', {
    style: 'currency',
    currency: 'AUD'
  }).format(parseFloat(value));
}

function formatDate(dateString) {
  return new Intl.DateTimeFormat('en-AU').format(new Date(dateString));
}

// Examples:
// formatCurrency('1500000') → "A$1,500,000.00"
// formatDate('2025-12-15') → "15/12/2025"
```

---

## Key Variables

```javascript
formState        // Current form values
validationRules  // Rules for each field
placeholders     // Mapping: placeholder → field name
children         // Array of docx paragraphs/tables

// Example usage:
const data = captureFormState();           // → formState
const validation = validateForm();         // → { isValid, errors }
generateTermSheetDocument();               // → uses data, validation, children
```

---

## Deployment Checklist

- [ ] All form fields have `data-field` attributes
- [ ] Validation rules cover all required fields
- [ ] Conditional sections tested and working
- [ ] Word template has all placeholders updated
- [ ] Document generation tested with sample data
- [ ] File sizes reasonable (< 100KB)
- [ ] Error messages are clear
- [ ] Draft auto-saves working
- [ ] Works in Chrome, Firefox, Safari, Edge
- [ ] Mobile responsive (if needed)

---

## Performance Tips

- Use `debounce()` for conditional handlers (avoid re-running on every keystroke)
- Cache DOM selectors: `const submitBtn = document.getElementById('submit');`
- Validate as user types, but only show errors on submit
- Generate document in worker thread if processing large forms

---

## That's it! 

Start with Phase 1, move through sequentially. Each phase builds on the previous.

**Expected timeline:** 2-3 weeks for full implementation.

**Questions?** Refer to the detailed guides:
- `term_sheet_process_guide.md` - Conceptual overview
- `term_sheet_implementation_guide.md` - Code implementations
- `IMPLEMENTATION_SUMMARY.md` - Full roadmap

**Good luck!** 🚀

