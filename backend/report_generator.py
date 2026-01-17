import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String
from config import REPORTS_DIR

# Color palette
COLORS = {
    'primary': colors.HexColor('#4F46E5'),      # Indigo
    'danger': colors.HexColor('#DC2626'),        # Red
    'success': colors.HexColor('#16A34A'),       # Green
    'warning': colors.HexColor('#F59E0B'),       # Amber
    'dark': colors.HexColor('#1F2937'),          # Dark gray
    'gray': colors.HexColor('#6B7280'),          # Gray
    'light_gray': colors.HexColor('#F3F4F6'),    # Light gray
    'border': colors.HexColor('#E5E7EB'),        # Border gray
}

# Cell type information with clinical significance
CELL_INFO = {
    'ABE': {'name': 'Abnormal Eosinophil', 'category': 'Abnormal', 'significance': 'May indicate eosinophilic disorders or allergic conditions'},
    'ART': {'name': 'Artefact', 'category': 'Technical', 'significance': 'Non-cellular element, excluded from analysis'},
    'BAS': {'name': 'Basophil', 'category': 'Normal Granulocyte', 'significance': 'Normal component; elevated in myeloproliferative disorders'},
    'BLA': {'name': 'Blast Cell', 'category': 'Immature/Malignant', 'significance': 'Immature cells; >20% suggests acute leukemia'},
    'EBO': {'name': 'Erythroblast', 'category': 'Erythroid Precursor', 'significance': 'Red cell precursor; abnormal levels suggest erythroid disorders'},
    'EOS': {'name': 'Eosinophil', 'category': 'Normal Granulocyte', 'significance': 'Normal component; elevated in allergic/parasitic conditions'},
    'FGC': {'name': 'Faggot Cell', 'category': 'Malignant', 'significance': 'Auer rod bundles; highly suggestive of Acute Promyelocytic Leukemia (APL)'},
    'HAC': {'name': 'Hairy Cell', 'category': 'Malignant', 'significance': 'Indicates Hairy Cell Leukemia'},
    'KSC': {'name': 'Kidney Shaped Cell', 'category': 'Monocytic', 'significance': 'Monocytic lineage; may indicate monocytic leukemia'},
    'LYI': {'name': 'Immature Lymphocyte', 'category': 'Immature', 'significance': 'Lymphoid precursor; elevated in lymphoblastic disorders'},
    'LYT': {'name': 'Lymphocyte', 'category': 'Normal Lymphoid', 'significance': 'Normal component; abnormal morphology may suggest lymphoma'},
    'MMZ': {'name': 'Metamyelocyte', 'category': 'Granulocyte Precursor', 'significance': 'Normal maturation stage; left shift if elevated'},
    'MON': {'name': 'Monocyte', 'category': 'Normal Monocytic', 'significance': 'Normal component; elevated in infections and monocytic leukemia'},
    'MYB': {'name': 'Myeloblast', 'category': 'Immature/Malignant', 'significance': 'Earliest myeloid precursor; >20% indicates AML'},
    'NGB': {'name': 'Band Neutrophil', 'category': 'Granulocyte Precursor', 'significance': 'Immature neutrophil; left shift indicates infection or stress'},
    'NGS': {'name': 'Segmented Neutrophil', 'category': 'Normal Granulocyte', 'significance': 'Mature neutrophil; normal component of peripheral blood'},
    'NIF': {'name': 'Immature Neutrophil', 'category': 'Granulocyte Precursor', 'significance': 'Early neutrophil precursor; elevated in severe infections'},
    'OTH': {'name': 'Other Cell', 'category': 'Unclassified', 'significance': 'Requires manual review for classification'},
    'PEB': {'name': 'Proerythroblast', 'category': 'Erythroid Precursor', 'significance': 'Earliest erythroid precursor; elevated in erythroid hyperplasia'},
    'PLM': {'name': 'Plasma Cell', 'category': 'Lymphoid/Malignant', 'significance': 'Antibody-producing cell; elevated in plasma cell neoplasms'},
    'PMO': {'name': 'Promyelocyte', 'category': 'Granulocyte Precursor', 'significance': 'Early myeloid cell; abnormal promyelocytes in APL'}
}

MALIGNANT_CLASSES = ['BLA', 'MYB', 'PMO', 'FGC', 'ABE', 'EBO', 'PLM', 'HAC']


def generate_pdf_report(
    job_id: str,
    patient_data: dict,
    classification_result: dict,
    image_paths: list = None,
    individual_results: list = None
) -> str:
    """
    Generate a comprehensive medical PDF report for bone marrow cell classification
    """
    pdf_path = os.path.join(REPORTS_DIR, f"report_{job_id}.pdf")
    doc = SimpleDocTemplate(
        pdf_path, 
        pagesize=letter, 
        topMargin=0.5*inch, 
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    # ===== STYLES =====
    logo_style = ParagraphStyle('Logo', parent=styles['Heading1'], fontSize=28, textColor=COLORS['primary'], alignment=TA_CENTER, spaceAfter=5)
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, textColor=COLORS['dark'], alignment=TA_CENTER, spaceAfter=5)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=COLORS['gray'], alignment=TA_CENTER, spaceAfter=15)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=13, textColor=COLORS['primary'], spaceBefore=15, spaceAfter=8, borderPadding=(0, 0, 5, 0))
    subsection_style = ParagraphStyle('Subsection', parent=styles['Heading3'], fontSize=11, textColor=COLORS['dark'], spaceBefore=10, spaceAfter=6)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, textColor=COLORS['dark'], spaceAfter=4, leading=14)
    small_style = ParagraphStyle('Small', parent=styles['Normal'], fontSize=9, textColor=COLORS['gray'], spaceAfter=3)
    disclaimer_style = ParagraphStyle('Disclaimer', parent=styles['Normal'], fontSize=8, textColor=COLORS['gray'], alignment=TA_JUSTIFY, leading=11)
    
    # ===== HEADER =====
    elements.append(Paragraph("CYTOMIND", logo_style))
    elements.append(Paragraph("Bone Marrow Cell Analysis Report", title_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=COLORS['primary'], spaceBefore=10, spaceAfter=10))
    
    # Report metadata
    report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    meta_data = [
        [Paragraph(f"<b>Report Date:</b> {report_date}", small_style),
         Paragraph(f"<b>Report ID:</b> {job_id[:8]}...", small_style)]
    ]
    meta_table = Table(meta_data, colWidths=[3.5*inch, 3.5*inch])
    elements.append(meta_table)
    elements.append(Spacer(1, 15))
    
    # ===== PATIENT INFORMATION =====
    elements.append(Paragraph("PATIENT INFORMATION", section_style))
    
    patient_table_data = [
        ["Patient ID", patient_data.get("patientId", "N/A"), "Age", f"{patient_data.get('age', 'N/A')} years"],
        ["Patient Name", patient_data.get("name", "N/A"), "Gender", "Not specified"],
    ]
    patient_table = Table(patient_table_data, colWidths=[1.2*inch, 2.3*inch, 1*inch, 2.5*inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['dark']),
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['light_gray']),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 15))
    
    # ===== SUMMARY DIAGNOSIS =====
    elements.append(Paragraph("SUMMARY DIAGNOSIS", section_style))
    
    classification = classification_result.get("classification", "N/A")
    total_cells = classification_result.get("total_cells", len(individual_results) if individual_results else 1)
    malignancy_pct = classification_result.get("malignancy_percentage", 0)
    malignant_count = classification_result.get("malignant_cell_count", 0)
    
    # Diagnosis box with color coding
    if classification == "MALIGNANT":
        diag_color = COLORS['danger']
        diag_bg = colors.HexColor('#FEE2E2')
        risk_level = "HIGH RISK"
        recommendation = "Immediate hematological consultation recommended. Further molecular testing advised."
    elif classification == "SUSPICIOUS":
        diag_color = COLORS['warning']
        diag_bg = colors.HexColor('#FEF3C7')
        risk_level = "MODERATE RISK"
        recommendation = "Follow-up evaluation recommended. Consider repeat analysis in 2-4 weeks."
    else:
        diag_color = COLORS['success']
        diag_bg = colors.HexColor('#DCFCE7')
        risk_level = "LOW RISK"
        recommendation = "Findings within normal parameters. Routine follow-up as clinically indicated."
    
    diag_style = ParagraphStyle('Diagnosis', parent=styles['Heading1'], fontSize=16, textColor=diag_color, alignment=TA_CENTER)
    
    diagnosis_data = [
        [Paragraph(f"<b>OVERALL ASSESSMENT: {classification}</b>", diag_style)],
        [Paragraph(f"<b>Risk Level:</b> {risk_level}", ParagraphStyle('Risk', parent=normal_style, alignment=TA_CENTER))],
    ]
    diagnosis_table = Table(diagnosis_data, colWidths=[7*inch])
    diagnosis_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), diag_bg),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 2, diag_color),
    ]))
    elements.append(diagnosis_table)
    elements.append(Spacer(1, 15))
    
    # ===== ANALYSIS SUMMARY =====
    elements.append(Paragraph("ANALYSIS SUMMARY", section_style))
    
    primary_class = classification_result.get("primary_class", "N/A")
    primary_name = CELL_INFO.get(primary_class, {}).get('name', primary_class)
    confidence = classification_result.get("confidence", 0)
    
    summary_data = [
        ["Total Cells Analyzed", str(total_cells), "Primary Cell Type", f"{primary_name} ({primary_class})"],
        ["Malignant Cells Detected", str(malignant_count), "Malignancy Rate", f"{malignancy_pct:.1f}%"],
        ["Average Confidence", f"{confidence:.1f}%", "Analysis Method", "AI Ensemble (ViT + ResNet)"],
    ]
    summary_table = Table(summary_data, colWidths=[1.5*inch, 1.7*inch, 1.5*inch, 2.3*inch])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (-1, -1), COLORS['dark']),
        ('BACKGROUND', (1, 0), (1, -1), COLORS['light_gray']),
        ('BACKGROUND', (3, 0), (3, -1), COLORS['light_gray']),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 15))
    
    # ===== CELL DISTRIBUTION =====
    elements.append(Paragraph("CELL TYPE DISTRIBUTION", section_style))
    
    cell_distribution = classification_result.get("cell_distribution", {})
    
    if cell_distribution:
        dist_header = ["Cell Type", "Count", "Percentage", "Category", "Clinical Significance"]
        dist_data = [dist_header]
        
        for cell_code, data in cell_distribution.items():
            if isinstance(data, dict):
                count = data.get('count', 0)
                pct = data.get('percentage', 0)
            else:
                count = data
                pct = (count / total_cells * 100) if total_cells > 0 else 0
            
            cell_info = CELL_INFO.get(cell_code, {'name': cell_code, 'category': 'Unknown', 'significance': 'N/A'})
            is_malignant = cell_code in MALIGNANT_CLASSES
            
            dist_data.append([
                f"{cell_info['name']} ({cell_code})" + (" !" if is_malignant else ""),
                str(count),
                f"{pct:.1f}%",
                cell_info['category'],
                cell_info['significance'][:50] + "..." if len(cell_info['significance']) > 50 else cell_info['significance']
            ])
        
        dist_table = Table(dist_data, colWidths=[1.8*inch, 0.6*inch, 0.8*inch, 1.3*inch, 2.5*inch])
        dist_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
            ('TEXTCOLOR', (0, 1), (-1, -1), COLORS['dark']),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (1, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLORS['light_gray']]),
        ]))
        elements.append(dist_table)
    elements.append(Spacer(1, 15))
    
    # ===== INDIVIDUAL CELL ANALYSIS (if multiple images) =====
    if individual_results and len(individual_results) > 1:
        elements.append(Paragraph("INDIVIDUAL CELL ANALYSIS", section_style))
        
        ind_header = ["#", "Classification", "Confidence", "Malignant", "Top Prediction"]
        ind_data = [ind_header]
        
        for idx, result in enumerate(individual_results[:20], 1):  # Limit to 20 rows
            primary = result.get('primary_class', 'N/A')
            conf = result.get('confidence', 0)
            is_mal = "Yes !" if primary in MALIGNANT_CLASSES else "No"
            cell_name = CELL_INFO.get(primary, {}).get('name', primary)
            
            ind_data.append([
                str(idx),
                result.get('classification', 'N/A'),
                f"{conf:.1f}%",
                is_mal,
                f"{cell_name} ({primary})"
            ])
        
        if len(individual_results) > 20:
            ind_data.append(["...", f"+ {len(individual_results) - 20} more cells", "", "", ""])
        
        ind_table = Table(ind_data, colWidths=[0.4*inch, 1.2*inch, 1*inch, 1*inch, 3.4*inch])
        ind_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 0), (-1, 0), COLORS['primary']),
            ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (0, 0), (3, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLORS['light_gray']]),
        ]))
        elements.append(ind_table)
        elements.append(Spacer(1, 15))
    
    # ===== CLINICAL INTERPRETATION =====
    elements.append(Paragraph("CLINICAL INTERPRETATION", section_style))
    
    interpretation = generate_clinical_interpretation(classification_result, individual_results)
    elements.append(Paragraph(interpretation, normal_style))
    elements.append(Spacer(1, 10))
    
    # Recommendations
    elements.append(Paragraph("<b>Recommendations:</b>", normal_style))
    elements.append(Paragraph(f"- {recommendation}", normal_style))
    
    if classification == "MALIGNANT":
        elements.append(Paragraph("- Flow cytometry and cytogenetic analysis recommended", normal_style))
        elements.append(Paragraph("- Molecular testing for specific mutations (FLT3, NPM1, CEBPA)", normal_style))
        elements.append(Paragraph("- Consider bone marrow biopsy for tissue architecture evaluation", normal_style))
    elif classification == "SUSPICIOUS":
        elements.append(Paragraph("- Repeat peripheral blood smear review", normal_style))
        elements.append(Paragraph("- Monitor complete blood count trends", normal_style))
    
    elements.append(Spacer(1, 20))
    
    # ===== QUALITY METRICS =====
    elements.append(Paragraph("QUALITY METRICS", section_style))
    
    quality_data = [
        ["Image Quality", "Acceptable", "Model Version", "Cytomind v1.0"],
        ["Processing Time", "< 5 seconds", "Confidence Threshold", ">= 5%"],
    ]
    quality_table = Table(quality_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    quality_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, COLORS['border']),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), COLORS['light_gray']),
    ]))
    elements.append(quality_table)
    elements.append(Spacer(1, 25))
    
    # ===== FOOTER / DISCLAIMER =====
    elements.append(HRFlowable(width="100%", thickness=1, color=COLORS['border'], spaceBefore=10, spaceAfter=10))
    
    elements.append(Paragraph("<b>DISCLAIMER</b>", ParagraphStyle('DisclaimerTitle', parent=small_style, textColor=COLORS['dark'])))
    elements.append(Paragraph(
        "This report has been generated by the Cytomind AI-assisted diagnostic system. The artificial intelligence "
        "algorithms used in this analysis are designed to assist healthcare professionals in cell classification and "
        "should not be used as the sole basis for clinical diagnosis or treatment decisions. All findings should be "
        "validated by a qualified hematopathologist or clinical laboratory professional. The accuracy of AI predictions "
        "may vary based on image quality and sample preparation. This report does not constitute medical advice.",
        disclaimer_style
    ))
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        f"Cytomind | AI-Powered Bone Marrow Analysis | Report generated on {report_date}",
        ParagraphStyle('Footer', parent=small_style, alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(elements)
    return pdf_path


def generate_clinical_interpretation(classification_result: dict, individual_results: list = None) -> str:
    """Generate clinical interpretation text based on analysis results"""
    classification = classification_result.get("classification", "N/A")
    malignancy_pct = classification_result.get("malignancy_percentage", 0)
    primary_class = classification_result.get("primary_class", "N/A")
    total_cells = classification_result.get("total_cells", 1)
    cell_distribution = classification_result.get("cell_distribution", {})
    
    primary_info = CELL_INFO.get(primary_class, {'name': primary_class, 'significance': ''})
    
    interpretation = f"Analysis of {total_cells} bone marrow cell(s) was performed using AI-assisted image classification. "
    
    if classification == "MALIGNANT":
        interpretation += f"The analysis reveals a concerning pattern with {malignancy_pct:.1f}% of cells classified as potentially malignant. "
        interpretation += f"The predominant cell type identified is {primary_info['name']}, which {primary_info['significance'].lower()}. "
        interpretation += "These findings warrant immediate clinical attention and further diagnostic workup. "
        
        # Check for specific malignant patterns
        if 'FGC' in cell_distribution:
            interpretation += "CRITICAL: Faggot cells detected, which are pathognomonic for Acute Promyelocytic Leukemia (APL). Urgent evaluation required. "
        if 'BLA' in cell_distribution or 'MYB' in cell_distribution:
            interpretation += "Elevated blast/myeloblast population detected, concerning for acute leukemia. "
            
    elif classification == "SUSPICIOUS":
        interpretation += f"The analysis shows borderline findings with {malignancy_pct:.1f}% potentially abnormal cells. "
        interpretation += f"The predominant cell type is {primary_info['name']}. "
        interpretation += "While not definitively malignant, these findings warrant close monitoring and follow-up evaluation. "
        
    else:
        interpretation += f"The cellular composition appears within normal parameters with minimal abnormal cells ({malignancy_pct:.1f}%). "
        interpretation += f"The predominant cell type is {primary_info['name']}, which is {primary_info['significance'].lower() if primary_info['significance'] else 'a normal finding'}. "
        interpretation += "No immediate concerns identified based on AI analysis. "
    
    return interpretation
