from xhtml2pdf import pisa as converter


def save_html_to_pdf(source_html, output_path):
    result_file = open(output_path, "w+b")

    conversion_status = converter.CreatePDF(
        source_html,
        dest=result_file)

    result_file.close()

    return conversion_status.err
