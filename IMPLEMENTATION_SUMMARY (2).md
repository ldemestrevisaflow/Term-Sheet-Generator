# Term Sheet Questionnaire → Document Generation: Executive Summary

## Quick Overview

You have two HTML files that need to work together:
1. **Term Sheet Questionnaire** (form input)
2. **Term Sheet Master Template** (Word document)

The process should flow:
```
User fills Questionnaire → Validation → Data captured → Document populated → Word file generated
```

Your existing Term Sheet Questionnaire is ~80% complete. It already has:
- ✓ Multi-section form with sidebar navigation
- ✓ Form fields with proper labels and validation indicators
- ✓ Progress tracking
- ✓ Draft save functionality
- ✓ Date pickers with Flatpickr
- ✓ Basic document generation using docx library

What needs to be enhanced:
- [ ] Standardize all form field IDs with `data-field` attributes
- [ ] Implement comprehensive validation rules
- [ ] Build conditional logic for dynamic sections
- [ ] Enhance document generation with proper formatting
- [ ] Add proper placeholder mapping to Word template

---

## Implementation Path (7 Phases)

### Phase 1: Architecture Planning
**Time: 2-3 hours**
- Map all form fields to data properties
- Identify template placeholders
- Define conditional sections
- Create validation rules matrix

**Deliverable:** Architecture document ✓ (Provided in `term_sheet_process_guide.md`)

---

### Phase 2: HTML Form Enhancement
**Time: 4-6 hours**
- Add `data-field="fieldName"` to every form input
- Implement data validation layer
- Add conditional visibility handlers
- Set up form state object

**Key Changes:**
```html
<!-- Before -->
<input type="text" id="companyName" placeholder="Company">

<!-- After -->
<input type="text" id="companyName" class="form-control" 
       data-field="companyName" placeholder="Company Name"
       aria-label="Company Name" required>
```

**Status:** Your HTML already has most fields; just standardize them.

---

### Phase 3: Data Management & Validation
**Time: 3-4 hours**
- Implement `captureFormState()` - collect all form values
- Implement `validateForm()` - validate before generation
- Implement `handleConditionals()` - show/hide sections dynamically
- Create validation rules configuration

**Key Functions (provided):**
- `captureFormState()` - captures form into object
- `populateFormFromData()` - restores form from saved object
- `validateForm()` - comprehensive validation with errors/warnings
- `validateABN()` - Australian Business Number validation
- `validateBusinessRules()` - cross-field logic validation

**Status:** Partially implemented in your HTML; needs enhancement.

---

### Phase 4: Word Document Template Preparation
**Time: 2-3 hours**
- Replace all static values with unique placeholders
- Use format: `<<PLACEHOLDER_NAME>>`
- Create placeholder-to-data mapping dictionary
- Test placeholder discovery

**Placeholders to add to Term Sheet template:**
```
<<TERM_SHEET_DATE>>
<<SELLER_NAME>>
<<BUYER_NAME>>
<<COMPANY_NAME>>
<<COMPANY_ABN>>
<<PURCHASE_PRICE>>
<<COMPLETION_DATE>>
<<DUE_DILIGENCE_DATE>>
<<BINDING_STATUS>>
<<JURISDICTION>>
<<GOVERNING_LAW>>
... (full list in implementation guide)
```

**Status:** Your Term Sheet template uses `[insert...]` format; convert to `<<...>>`

---

### Phase 5: Document Generation Engine
**Time: 6-8 hours**
- Implement `generateTermSheetDocument()` - main generation function
- Build `generateConditionalSections()` - create dynamic content
- Create helper functions for formatting (currency, dates, etc.)
- Implement table generation for schedules and details

**Core Logic:**
1. Validate form (Phase 3)
2. Capture form state (Phase 3)
3. Create document structure (Phase 5)
4. Add conditional sections (Phase 5)
5. Apply formatting (Phase 5)
6. Generate .docx file (Phase 5)
7. Trigger download (Phase 5)

**Status:** Your HTML has basic generation; needs full implementation.

---

### Phase 6: Testing & Quality Assurance
**Time: 4-5 hours**
- Test all conditional paths
- Verify placeholder replacement
- Check formatting in generated documents
- Test edge cases (empty fields, long text, special characters)
- Verify with actual Word documents

**Test Cases:**
- [ ] Generate binding term sheet
- [ ] Generate non-binding term sheet
- [ ] With and without due diligence
- [ ] With various schedule combinations
- [ ] With maximum data length
- [ ] With empty optional fields

**Status:** Your HTML has basic testing; needs comprehensive QA.

---

### Phase 7: Integration & Optimization
**Time: 2-3 hours**
- Extract reusable utilities into shared module
- Integrate with existing TSA/TFA generator
- Add audit trail logging
- Optimize performance
- Add draft versioning

**Reusable Utilities:**
- Form handling (capture, populate, validate)
- Document utilities (format, generate, save)
- UI utilities (toast, progress, conditionals)

---

## Key Code Patterns

### 1. Form Field Standardization
```html
<input type="text" 
       id="fieldId"
       class="form-control" 
       data-field="fieldId"           <!-- KEY: This attribute -->
       placeholder="User hint"
       aria-label="Accessible label"
       required>                        <!-- Add for required fields -->
```

### 2. Form State Management
```javascript
// Capture
const data = captureFormState();
// Returns: { companyName: "Acme", purchasePrice: "1500000", ... }

// Populate
populateFormFromData(data);
// Sets all form fields from object
```

### 3. Validation
```javascript
// Validate entire form
const validation = validateForm();
if (!validation.isValid) {
  console.log(validation.errors);  // ['Error 1', 'Error 2']
  console.log(validation.warnings); // ['Warning 1']
  return;
}
```

### 4. Conditional Sections
```javascript
// In form HTML
<section id="section-exclusivity" style="display:none;">
  <!-- Exclusivity fields -->
</section>

// In JavaScript
function handleConditionals() {
  const data = captureFormState();
  document.getElementById('section-exclusivity').style.display = 
    data.exclusivityRequired === 'yes' ? 'block' : 'none';
}
```

### 5. Document Generation
```javascript
// Capture validated data
const data = captureFormState();

// Build document sections
const children = [
  new docx.Paragraph({ text: 'TITLE', heading: docx.HeadingLevel.HEADING_1 }),
  new docx.Paragraph({ text: data.companyName }),
  // ... more sections
];

// Create and save
const doc = new docx.Document({ sections: [{ children }] });
docx.Packer.toBlob(doc).then(blob => saveAs(blob, filename));
```

---

## Comparison: Your Current vs. Required State

| Aspect | Current | Required |
|--------|---------|----------|
| Form Fields | Mostly complete | All need `data-field` attribute |
| Validation | Basic date validation | Comprehensive validation rules |
| Conditionals | Some sections hidden | Full conditional logic for all paths |
| Document Generation | Generates basic doc | Generates formatted doc with all sections |
| Placeholder Mapping | Direct text replacement | Structured mapping object |
| Error Handling | Basic toasts | Detailed error display with highlighting |
| Draft Persistence | localStorage implemented | Enhanced with versioning |
| Quality Assurance | Minimal | Comprehensive test cases |

---

## Integration with Your TSA/TFA Generator

Your TSA/TFA generator likely has similar patterns. Recommended approach:

1. **Extract Shared Utilities:**
   - `form-utils.js` - Form capture, populate, validate
   - `document-utils.js` - Format, generate, save
   - `ui-utils.js` - Toast, progress, conditionals

2. **Create Tool-Specific Files:**
   - `term-sheet-generator.js` - Term sheet logic
   - `tsa-tfa-generator.js` - TSA/TFA logic (refactored)

3. **Architecture:**
   ```
   /lib/
   ├── form-utils.js
   ├── document-utils.js
   └── ui-utils.js
   
   /tools/
   ├── term-sheet/
   │  ├── index.html
   │  └── generator.js
   ├── tsa-tfa/
   │  ├── index.html
   │  └── generator.js
   ```

4. **Usage:**
   ```html
   <!-- In both HTML files -->
   <script src="../lib/form-utils.js"></script>
   <script src="../lib/document-utils.js"></script>
   <script src="../lib/ui-utils.js"></script>
   <script src="generator.js"></script>
   ```

---

## Timeline Estimate

| Phase | Hours | Week |
|-------|-------|------|
| 1: Architecture | 3 | Week 1 |
| 2: HTML Enhancement | 5 | Week 1 |
| 3: Data Management | 4 | Week 1 |
| 4: Template Prep | 3 | Week 2 |
| 5: Document Generation | 7 | Week 2 |
| 6: Testing | 4 | Week 2 |
| 7: Integration | 3 | Week 3 |
| **TOTAL** | **29 hours** | **3 weeks** |

**Realistic estimate:** 4-5 weeks with thorough QA and documentation.

---

## Immediate Next Steps

### Week 1 - Foundations
1. **Monday-Tuesday:** Review this guide + Phase architecture
2. **Tuesday-Wednesday:** Standardize all form field `data-field` attributes
3. **Wednesday-Thursday:** Implement data validation layer
4. **Thursday-Friday:** Implement conditional visibility logic

### Week 2 - Document Generation
1. **Monday:** Prepare Word template with placeholders
2. **Tuesday-Wednesday:** Implement core document generation
3. **Thursday:** Add conditional sections
4. **Friday:** Testing and bug fixes

### Week 3 - Refinement
1. **Monday-Tuesday:** Integration with TSA/TFA generator
2. **Wednesday:** Performance optimization
3. **Thursday-Friday:** Final QA and documentation

---

## Critical Success Factors

1. ✅ **Standardized Form Fields** - All inputs need `data-field` attribute
2. ✅ **Comprehensive Validation** - Catch errors before generation
3. ✅ **Proper Conditionals** - Show/hide sections based on user input
4. ✅ **Placeholder Mapping** - Every template placeholder must have a rule
5. ✅ **Formatting Consistency** - Currency, dates, etc. formatted uniformly
6. ✅ **Error Handling** - Clear messages for validation failures
7. ✅ **Testing** - All conditional paths tested with real data

---

## Common Pitfalls to Avoid

❌ **Not standardizing form field names**
- Each tool uses different naming conventions
- Solution: Use consistent `data-field="camelCase"` everywhere

❌ **Incomplete validation**
- Only validating at generation time
- Solution: Validate as user types, show visual feedback

❌ **Hardcoded conditional logic**
- Multiple if/else statements scattered in code
- Solution: Use configuration-driven approach

❌ **Poor error messages**
- Generic "Error occurred" messages
- Solution: Specific, actionable error messages

❌ **No test coverage**
- Flying blind with changes
- Solution: Document all test cases, rerun after changes

❌ **Skipping draft persistence**
- Users lose work on page refresh
- Solution: Auto-save to localStorage every 30 seconds

---

## References & Resources

**Included Documents:**
1. `term_sheet_process_guide.md` - 7-phase implementation guide
2. `term_sheet_implementation_guide.md` - Code snippets for each phase
3. `term_sheet_process_flow.md` - Visual process flows and data mapping

**External Libraries:**
- [docx.js Documentation](https://docx.js.org/)
- [Flatpickr Date Picker](https://flatpickr.js.org/)
- [FileSaver.js for Downloads](https://github.com/eligrey/FileSaver.js/)

**Your Existing Code:**
- `Term_Sheet_Questionnaire__7_.html` - Current implementation (80% complete)
- `Term_Sheet_-_Share_Sale__ID_2740_.docx` - Master template to populate

---

## Success Metrics

Track these metrics as you implement:

- [ ] All form fields have `data-field` attributes
- [ ] Validation catches 100% of test case errors
- [ ] All 5+ conditional paths tested and working
- [ ] Generated documents have correct formatting
- [ ] No placeholder appears in final document
- [ ] Error messages are clear and actionable
- [ ] Draft auto-saves every 30 seconds
- [ ] Processing time < 2 seconds
- [ ] File sizes reasonable (< 100KB)
- [ ] Works across browsers (Chrome, Firefox, Safari, Edge)

---

## Summary

You're at 80% completion. The questionnaire form is solid. Now you need to:

1. **Standardize form fields** (5 hours)
2. **Enhance validation** (4 hours)
3. **Build conditionals** (6 hours)
4. **Prepare template** (3 hours)
5. **Generate documents** (7 hours)
6. **Test thoroughly** (4 hours)
7. **Integrate & optimize** (3 hours)

**Total: 32 hours across 3-4 weeks**

This is a high-impact tool that will streamline your Term Sheet generation process. The effort is worth it for the time savings you'll achieve.

---

## Questions & Support

As you implement, refer to:
- **Conceptual questions?** → Check `term_sheet_process_guide.md`
- **Code examples?** → Check `term_sheet_implementation_guide.md`
- **Process flows?** → Check `term_sheet_process_flow.md`
- **Specific functions?** → See implementation guide code snippets

**Good luck! You've got this.** 🚀

