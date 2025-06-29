from chamas.models import *
from django.http import JsonResponse,HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle,getSampleStyleSheet
from reportlab.platypus             import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Table, TableStyle, Spacer
)

class DownloadService:
    @staticmethod
    def download_loan_report(request,chama_id):
        chama = Chama.objects.get(pk=chama_id)
        loans = LoanItem.objects.filter(chama=chama)

        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{chama.name}_loan_report.pdf"'
        )

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        
        def draw_header(canvas, doc):
            canvas.saveState()
            # Main title
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-40,
                chama.name
            )
            # Subtitle and date
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-60,
                "Loan Report"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-75,
                datetime.now().strftime("%Y-%m-%d")
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

    
        data = [[
            'Member Name', 'Loan Type',
            'Start Date', 'Due Date',
            'Amount', 'Total Paid',
            'Balance', 'Status'
        ]]
        for loan in loans:
            data.append([
                loan.member.name,
                loan.type.name,
                loan.start_date.strftime('%Y-%m-%d'),
                loan.end_date.strftime('%Y-%m-%d'),
                f'ksh {loan.amount}',
                f'ksh {loan.total_paid}',
                f'ksh {loan.balance}',
                loan.status,
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

    
        story = [
            Spacer(1, 40),  # space below header
            table
        ]
        doc.build(story)
        return response
    
    @staticmethod
    def download_loan_repayment_schedule(chama_id):
        # 1) Fetch Chama and active Loans
        chama = Chama.objects.get(pk=chama_id)
        loans = LoanItem.objects.filter(chama=chama, status='active')

        # 2) Prepare PDF response & BaseDocTemplate
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{chama.name}_loan_repayment_schedule.pdf"'
        )

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        # 3) Header callback for every page
        def draw_header(canvas, doc):
            canvas.saveState()
            # Main title
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-40,
                chama.name
            )
            # Subtitle and date
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-60,
                "Loan Repayment Schedule"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-75,
                datetime.now().strftime("%Y-%m-%d")
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

        # 4) Build table data & style
        data = [[
            'Member Name', 'Loan Type', 'Start Date',
            'Due Date', 'Amount', 'Total Paid',
            'Balance', 'Status', 'Repayment Term'
        ]]
        for loan in loans:
            data.append([
                loan.member.name,
                loan.type.name,
                loan.start_date.strftime('%Y-%m-%d'),
                loan.end_date.strftime('%Y-%m-%d'),
                f'ksh {loan.amount}',
                f'ksh {loan.total_paid}',
                f'ksh {loan.balance}',
                loan.status,
                loan.due,
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

        # 5) Assemble & build
        story = [
            Spacer(1, 40),  # space below header
            table
        ]
        doc.build(story)
        return response
    
    @staticmethod
    def download_group_investment_income(chama_id):
        # 1) Fetch Chama and group Income data
        chama   = Chama.objects.get(pk=chama_id)
        incomes = Income.objects.filter(chama=chama, forGroup=True)

        # 2) Prepare PDF response & BaseDocTemplate
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{chama.name}_group_investment_income.pdf"'
        )

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        # 3) Header callback for every page
        def draw_header(canvas, doc):
            canvas.saveState()
            # Main title
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-40,
                chama.name
            )
            # Subtitle and date
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-60,
                "Group Investment Income"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-75,
                datetime.now().strftime("%Y-%m-%d")
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

        # 4) Build table data & style
        data = [[
            'Income Name', 'Investment',
            'Date', 'Amount'
        ]]
        for inc in incomes:
            data.append([
                inc.name,
                inc.investment.name,
                inc.date.strftime('%Y-%m-%d'),
                f'ksh {inc.amount}',
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

        # 5) Assemble & build
        story = [
            Spacer(1, 40),  # space below header
            table
        ]
        doc.build(story)
        return response
    
    @staticmethod
    def download_member_investment_income(request,chama_id):
        # 1) Fetch Chama and Income data
        chama = Chama.objects.get(pk=chama_id)
        member_id = request.GET.get('member-id', None)

        if member_id:
            member = ChamaMember.objects.get(pk=int(member_id))
            incomes = Income.objects.filter(chama=chama, forGroup=False, owner=member)
        else:
            incomes = Income.objects.filter(chama=chama, forGroup=False)

        # 2) Prepare PDF response & BaseDocTemplate
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{chama.name}_member_investment_income.pdf"'
        )

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        # 3) Header callback for every page
        def draw_header(canvas, doc):
            canvas.saveState()
            # Main title
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 40,
                chama.name
            )
            # Subtitle and date
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 60,
                "Member Investment Income"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 75,
                datetime.now().strftime("%Y-%m-%d")
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

        # 4) Build table data & style
        data = [[
            'Income Name', 'Member Name',
            'Investment', 'Amount', 'Date'
        ]]
        for income in incomes:
            data.append([
                income.name,
                income.owner.name,
                income.investment.name,
                f'ksh {income.amount}',
                income.date.strftime('%Y-%m-%d')
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

        # 5) Assemble & build
        story = [
            Spacer(1, 40),  # space below header
            table
        ]
        doc.build(story)
        return response
    
    @staticmethod
    def download_individual_saving_report(request,chama_id):
        # 1) Fetch Chama and individual saving data
        chama = Chama.objects.get(pk=chama_id)
        member_id = request.GET.get('member-id', None)

        if member_id:
            member  = ChamaMember.objects.get(pk=int(member_id))
            savings = Saving.objects.filter(chama=chama, forGroup=False, owner=member)
        else:
            savings = Saving.objects.filter(chama=chama, forGroup=False)

        # 2) Prepare PDF response & BaseDocTemplate
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{chama.name}_individual_savings_report.pdf"'
        )

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='main'
        )

        # 3) Header callback for every page
        def draw_header(canvas, doc):
            canvas.saveState()
            # Main title
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-40,
                chama.name
            )
            # Subtitle and date
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-60,
                "Individual Savings Report"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-75,
                datetime.now().strftime('%Y-%m-%d')
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

        # 4) Build table data & style
        data = [[
            'Member', 'Amount', 'Type', 'Date'
        ]]
        for s in savings:
            data.append([
                s.owner.name,
                f'ksh {s.amount}',
                s.saving_type.name,
                s.date.strftime('%Y-%m-%d')
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

        # 5) Assemble & build document
        story = [
            Spacer(1, 40),  # space below header
            table
        ]
        doc.build(story)
        return response
    
    @staticmethod
    def download_group_saving_report(request,chama_id):
        # 1) Fetch Chama and group Saving data
        chama   = Chama.objects.get(pk=chama_id)
        savings = Saving.objects.filter(chama=chama, forGroup=True)

        # 2) Prepare PDF response & BaseDocTemplate
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{chama.name}_group_savings_report.pdf"'
        )

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        # 3) Header callback for every page
        def draw_header(canvas, doc):
            canvas.saveState()
            # Main title
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-40,
                chama.name
            )
            # Subtitle and date
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-60,
                "Group Savings Report"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0]/2, letter[1]-75,
                datetime.now().strftime('%Y-%m-%d')
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

        # 4) Build table data & style
        data = [[
            'Amount', 'Type', 'Date'
        ]]
        for s in savings:
            data.append([
                f'ksh {s.amount}',
                s.saving_type.name,
                s.date.strftime('%Y-%m-%d')
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

        # 5) Assemble & build
        story = [
            Spacer(1, 40),  # space below header
            table
        ]
        doc.build(story)
        return response
    
    @staticmethod
    def download_group_contributions_report(chama_id,contribution_id):
        # ─────────────────────────────────────────────
        # 1) Fetch & flatten your contribution records
        # ─────────────────────────────────────────────
        chama = Chama.objects.get(pk=chama_id)
        contribution = Contribution.objects.filter(chama=chama,id=contribution_id).first()
        contributions = []
        contributions.extend(contribution.records.all())
        contributions = sorted(
            contributions,
            key=lambda x: x.date_created,
            reverse=True
        )

        # ─────────────────────────────────────────────
        # 2) Prepare HTTP + PDF document
        # ─────────────────────────────────────────────
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{chama.name}_group_contributions_report.pdf"'
        )

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        # ─────────────────────────────────────────────
        # 3) Define header callback (runs on every page)
        # ─────────────────────────────────────────────
        def draw_header(canvas, doc):
            canvas.saveState()
            # Main title
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0]/2, letter[1] - 40,
                chama.name
            )
            # Subtitle and date
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0]/2, letter[1] - 60,
                f"Group Contributions Report for '{contribution.name}'"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0]/2, letter[1] - 75,
                datetime.now().strftime("%Y-%m-%d")
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])


        data = [[
            'Member', 'Contribution Type', 'Date',
            'Expected Amount', 'Amount Paid', 'Balance'
        ]]
        for c in contributions:
            data.append([
                c.member.name,
                c.contribution.name,
                c.date_created.strftime('%Y-%m-%d'),
                f'ksh {c.amount_expected}',
                f'ksh {c.amount_paid}',
                f'ksh {c.balance}',
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

    
        story = [
            Spacer(1, 40),  # gives some space below header
            table
        ]
        doc.build(story)
        return response
    
    @staticmethod
    def download_member_contribution_report(chama_id,member_id,scheme_id):
        # 1) Retrieve Chama and Member
        chama  = Chama.objects.get(pk=chama_id)
        member = ChamaMember.objects.get(pk=member_id)

        # 2) Collect this member's contributions
        contribution = Contribution.objects.filter(chama=chama,id=scheme_id).first()
        contributions = []

        for contrib in contribution.records.all():
            if contrib.member == member:
                contributions.append(contrib)

        # 3) Prepare PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{chama.name}_{member.name}_contribution_report.pdf"'
        )

        # 4) Setup BaseDocTemplate with header on each page
        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        # Header callback
        def draw_header(canvas, doc):
            canvas.saveState()
            # Title line
            canvas.setFont('Times-Bold', 14)
            canvas.drawCentredString(
                letter[0]/2, letter[1] - 40,
                f"Member Contribution Report - {member.name} - for '{contribution.name}'"
            )
            # Date line
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0]/2, letter[1] - 55,
                datetime.now().strftime('%Y-%m-%d')
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

        # 5) Build table data
        data = [[
            'Name', 'Contribution Type', 'Date',
            'Expected Amount', 'Amount Paid', 'Balance'
        ]]
        for contrib in contributions:
            data.append([
                contrib.member.name,
                contrib.contribution.name,
                contrib.date_created.strftime('%Y-%m-%d'),
                f'ksh {contrib.amount_expected}',
                f'ksh {contrib.amount_paid}',
                f'ksh {contrib.balance}'
            ])

        # 6) Create table with repeating header row
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

        # 7) Build story
        story = [
            Spacer(1, 40),
            table
        ]
        doc.build(story)
        return response
    
    @staticmethod
    def download_collected_fine_report(chama_id):
        # 1) Fetch Chama and cleared fines
        chama = Chama.objects.get(pk=chama_id)
        # Pull all fines with status 'cleared' in a single queryset
        fines = FineItem.objects.filter(fine_type__chama=chama, status='cleared')

        # 2) Prepare PDF response & BaseDocTemplate
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{chama.name}_collected_fines_report.pdf"'
        )

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        # 3) Header callback for every page
        def draw_header(canvas, doc):
            canvas.saveState()
            # Main title
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 40,
                chama.name
            )
            # Subtitle and date
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 60,
                "Collected Fines Report"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 75,
                datetime.now().strftime('%Y-%m-%d')
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

        # 4) Build table data
        data = [[
            'Member', 'Type', 'Amount', 'Paid Amount',
            'Balance', 'Status', 'Created', 'Last Updated'
        ]]
        for fine in fines:
            data.append([
                fine.member.name,
                fine.fine_type.name,
                f'ksh {fine.fine_amount}',
                f'ksh {fine.paid_fine_amount}',
                f'ksh {fine.fine_balance}',
                fine.status,
                fine.created.strftime('%Y-%m-%d'),
                fine.last_updated.strftime('%Y-%m-%d')
            ])

        # 5) Create table with header row repeated
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

        # 6) Assemble and build document
        story = [
            Spacer(1, 40),  # space below header
            table
        ]
        doc.build(story)
        return response
    
    @staticmethod
    def download_uncollected_fines_report(chama_id):
        # 1) Fetch Chama and active fines
        chama = Chama.objects.get(pk=chama_id)
        fines = FineItem.objects.filter(fine_type__chama=chama, status='active')

        # 2) Prepare PDF response & BaseDocTemplate
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{chama.name}_uncollected_fines_report.pdf"'
        )

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        # 3) Header callback for every page
        def draw_header(canvas, doc):
            canvas.saveState()
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 40,
                chama.name
            )
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 60,
                "Uncollected Fines Report"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 75,
                datetime.now().strftime('%Y-%m-%d')
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

        # 4) Build table data
        data = [[
            'Member', 'Type', 'Amount', 'Paid Amount',
            'Balance', 'Status', 'Created', 'Last Updated'
        ]]
        for fine in fines:
            data.append([
                fine.member.name,
                fine.fine_type.name,
                f'ksh {fine.fine_amount}',
                f'ksh {fine.paid_fine_amount}',
                f'ksh {fine.fine_balance}',
                fine.status,
                fine.created.strftime('%Y-%m-%d'),
                fine.last_updated.strftime('%Y-%m-%d')
            ])

        # 5) Create table with header row repeated
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

        # 6) Assemble and build document
        story = [
            Spacer(1, 40),
            table
        ]
        doc.build(story)
        return response
    
    @staticmethod
    def download_cashflow_report(chama_id):
         # 1) Fetch Chama and Cashflow Report data
        chama = Chama.objects.get(pk=chama_id)
        reports = CashflowReport.objects.filter(chama=chama).order_by('-date_created')

        # 2) Prepare PDF response & BaseDocTemplate
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{chama.name}_cashflow_report.pdf"'
        )

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        # 3) Header callback for every page
        def draw_header(canvas, doc):
            canvas.saveState()
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 40,
                chama.name
            )
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 60,
                "Cashflow Report"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 75,
                datetime.now().strftime('%Y-%m-%d')
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

        # 4) Build table data
        data = [['Member', 'Type', 'Amount', 'Date Created']]
        for report in reports:
            member_name = report.member.name if report.member else 'Group'
            data.append([
                member_name,
                report.type,
                f'ksh {report.amount}',
                report.object_date.strftime('%Y-%m-%d')
            ])

        # 5) Create table with header row repeated
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

        # 6) Assemble and build document
        story = [
            Spacer(1, 40),
            table
        ]
        doc.build(story)
        return response
    
    @staticmethod
    def download_member_cahsflow_report(chama_id,member_id):
        # 1) Fetch Chama, Member, and Cashflow Report data
        chama  = Chama.objects.get(pk=chama_id)
        member = ChamaMember.objects.get(pk=member_id)
        reports = CashflowReport.objects.filter(chama=chama, member=member).order_by('-date_created')

        # 2) Prepare PDF response & BaseDocTemplate
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="{member.name}_cashflow_report.pdf"'
        )

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        # 3) Header callback for every page
        def draw_header(canvas, doc):
            canvas.saveState()
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 40,
                chama.name
            )
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 60,
                f"{member.name} Cashflow Report"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 75,
                datetime.now().strftime('%Y-%m-%d')
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

        # 4) Build table data
        data = [['Member', 'Type', 'Amount', 'Date Created']]
        for report in reports:
            data.append([
                report.member.name,
                report.type,
                f'ksh {report.amount}',
                report.date_created.strftime('%Y-%m-%d')
            ])

        # 5) Create table with header row repeated
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

        # 6) Assemble and build document
        story = [
            Spacer(1, 40),
            table
        ]
        doc.build(story)
        return response
    
    @staticmethod
    def download_my_cashflow_report(request,chama_id):
        # 1) Fetch Chama and current user's member record
        chama = Chama.objects.get(pk=chama_id)
        try:
            user_member = chama.member.get(user=request.user)
        except ChamaMember.DoesNotExist:
            return HttpResponse("You are not a member of this chama.", status=403)

        # 2) Fetch Cashflow Reports
        reports = CashflowReport.objects.filter(chama=chama, member=user_member).order_by('-date_created')

        # 3) Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="my_cashflow_report.pdf"'

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        # 4) Header callback for every page
        def draw_header(canvas, doc):
            canvas.saveState()
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 40,
                chama.name
            )
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 60,
                "My Cashflow Report"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 75,
                datetime.now().strftime('%Y-%m-%d')
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

        # 5) Build table data
        data = [['Member', 'Type', 'Amount', 'Date Created']]
        for report in reports:
            data.append([
                report.member.name,
                report.type,
                f'ksh {report.amount}',
                report.date_created.strftime('%Y-%m-%d')
            ])

        # 6) Create and style table
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

        # 7) Assemble and build document
        story = [
            Spacer(1, 40),
            table
        ]
        doc.build(story)

        return response
    
    @staticmethod
    def download_expense_report(chama_id):
        # 1) Retrieve Chama and expenses
        chama = Chama.objects.get(pk=chama_id)
        expenses = Expense.objects.filter(chama=chama).order_by('-created_on')

        # 2) Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="expense_report.pdf"'

        doc = BaseDocTemplate(
            response,
            pagesize=letter,
            leftMargin=36, rightMargin=36,
            topMargin=72, bottomMargin=36
        )
        frame = Frame(
            doc.leftMargin, doc.bottomMargin,
            doc.width, doc.height,
            id='normal'
        )

        # 3) Header callback
        def draw_header(canvas, doc):
            canvas.saveState()
            canvas.setFont('Times-Bold', 16)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 40,
                chama.name
            )
            canvas.setFont('Times-Bold', 12)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 60,
                "Expense Report"
            )
            canvas.setFont('Times-Roman', 10)
            canvas.drawCentredString(
                letter[0] / 2, letter[1] - 75,
                datetime.now().strftime('%Y-%m-%d')
            )
            canvas.restoreState()

        doc.addPageTemplates([
            PageTemplate(id='WithHeader', frames=frame, onPage=draw_header)
        ])

        # 4) Define table data
        data = [['Name', 'Created By', 'Created On', 'Amount']]
        for expense in expenses:
            data.append([
                expense.name,
                expense.created_by.name if expense.created_by else '',
                expense.created_on.strftime('%Y-%m-%d') if expense.created_on else '',
                f'ksh {expense.amount}'
            ])

        # 5) Create and style table
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR',    (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN',        (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME',     (0, 0), (-1, 0), 'Times-Bold'),
            ('BOTTOMPADDING',(0, 0), (-1, 0), 12),
            ('GRID',         (0, 0), (-1, -1), 1, colors.black),
        ]))

        # 6) Assemble and build document
        story = [
            Spacer(1, 40),
            table
        ]
        doc.build(story)

        return response


                    









