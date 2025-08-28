import os

from packtools import data_checker
from packtools.sps.formats.pdf.pipeline import docx
from packtools.sps.formats.pdf.utils import file_utils
from packtools.sps.formats.pdf.pipeline.xml import extract_article_main_language
from packtools.sps.utils import xml_utils

from xml_manager import exceptions


def validate_xml_document(xml_file_path, output_root_dir, params):
    if not os.path.exists(output_root_dir):
        os.makedirs(output_root_dir)
        
    base_fname, fext = os.path.splitext(os.path.basename(xml_file_path))
    path_csv = os.path.join(output_root_dir, f'{base_fname}.validation.csv')
    path_exceptions = os.path.join(output_root_dir, f'{base_fname}.exceptions.json')

    try:
        validator = data_checker.XMLDataChecker(path_csv, path_exceptions, xml_file_path)
        validator.validate(params=params, csv_per_xml=False)
    except Exception as e:
        raise exceptions.XML_File_Validation_Error(f"Error during XML validation: {e}")

    return path_csv, path_exceptions


def generate_pdf_for_xml_document(xml_file_path, output_root_dir, params):
    if not os.path.exists(output_root_dir):
        os.makedirs(output_root_dir)

    if not isinstance(params, dict):
        params = {
            'base_layout': '/app/docx_layouts/layout.docx',
            'libreoffice_binary': 'libreoffice',
        }

    if 'base_layout' not in params:
        params['base_layout'] = '/app/docx_layouts/layout.docx'

    try:
        xml_tree = xml_utils.get_xml_tree(xml_file_path)
    except Exception as e:
        raise exceptions.XML_File_Parsing_Error(f"Error parsing XML file: {e}")

    try:
        docx_document = docx.pipeline_docx(xml_tree, data=params)
    except Exception as e:
        raise exceptions.XML_File_DOCX_Generation_Error(f"Error converting XML to DOCX: {e}")
    
    main_language = extract_article_main_language(xml_tree) or params.get('main_language', 'pt')
    
    base_name = os.path.basename(xml_file_path)
    f_name, f_ext = os.path.splitext(base_name)
    path_docx = os.path.join(output_root_dir, f'{f_name}.docx')
    path_pdf = os.path.join(output_root_dir, f'{f_name}.pdf')

    docx_document.save(path_docx)
    
    try:
        file_utils.convert_docx_to_pdf(path_docx, libreoffice_binary=params.get('libreoffice_binary', 'libreoffice'))
    except Exception as e:
        raise exceptions.XML_File_PDF_Generation_Error(f"Error generating PDF from DOCX: {e}")
        
    return path_pdf, path_docx, main_language


def generate_html_for_xml_document(xml_file_path, output_root_dir, config):
    if not os.path.exists(output_root_dir):
        os.makedirs(output_root_dir)

    # ToDo: Implement HTML generation logic here
    return