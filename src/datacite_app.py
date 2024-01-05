import os
import ipywidgets as widgets
from ipywidgets_jsonschema import Form
from IPython.display import display, SVG
from IPython.display import IFrame
from IPython import display as dsp
from datacite import DataCiteRESTClient, DataCiteMDSClient, schema43
import json

from dotenv import load_dotenv

load_dotenv()

class datacite_gui(object):
    def __init__(self):

        self.appname = 'datacite'
        self.author = 'rug'
        self.dspver = '0.0.1'
        
        self.datacite_user = os.getenv('API_USERNAME')
        self.datacite_pass = os.getenv('API_PASSWORD')
        self.datacite_doi_pre = os.getenv('DOI_PREFIX')
        
        self.dataciteconn = DataCiteRESTClient(
            username=self.datacite_user,
            password=self.datacite_pass,
            prefix=self.datacite_doi_pre,
            test_mode=True
        )

        self.dataciteMDS = DataCiteMDSClient(
            username=self.datacite_user,
            password=self.datacite_pass,
            prefix=self.datacite_doi_pre,
            test_mode=True
        )
        
        self.declare_widgets()
        self.observe_and_click()
                    
        # ipywidgets
        
    def get_schema(self):
        """This function loads the given schema available"""
        with open('datacite_schema.json', 'r') as file:
            schema = json.load(file)
        return schema
        
    def declare_widgets(self):
        self.output_form = widgets.Output()
        self.output_results = widgets.Output()
        
        self.datacite_user = widgets.Text(   
            value=None,  
            placeholder='Datacite user',
            description='Username:',
            disabled=False   
        )
        
        self.datacite_prefix = widgets.Text(   
            value=None,  
            placeholder='DOI prefix',
            description='Prefix:',
            disabled=False   
        )
        
        self.datacite_pass = widgets.Password(
            value=None,
            placeholder='Enter password',
            description='Password:',
            disabled=False
        )
        
        self.button_draft_doi = widgets.Button(
            description='Draft DOI',
            disabled=False,
            button_style='', # 'success', 'primary' 'info', 'warning', 'danger' or ''
            tooltip='Creates a draft DOI',
            icon='check' # (FontAwesome names without the `fa-` prefix)
        )

        self.button_doi_metadata = widgets.Button(
            description='DOI Metadata',
            disabled=False,
            button_style='', # 'success', 'primary' 'info', 'warning', 'danger' or ''
            tooltip='Get DOI metadata',
            # icon='check' # (FontAwesome names without the `fa-` prefix)
        )

        self.button_metadata_post = widgets.Button(
            description='Metadata post',
            disabled=False,
            button_style='', # 'success', 'primary' 'info', 'warning', 'danger' or ''
            tooltip='Metadata post',
            # icon='check' # (FontAwesome names without the `fa-` prefix)
        )
        
        tabChildren = [self.output_form, self.output_results]
        self.tab = widgets.Tab()
        self.tab.children = tabChildren
        self.tab.titles = ["Metadata", "Results"]
         
        self.fschema = self.get_schema()
    
        self.tab.selected_index = 0
        self.jsform = Form(self.fschema)
        with self.output_form:
            self.output_form.clear_output()
            self.jsform.show(width="600px")
        
        self.header = widgets.HTML("<h1>Datacite DOI prototype</h1>", layout=widgets.Layout(height='auto'))
        self.header.style.text_align='center'

        self.lsidebar = widgets.VBox(children = [self.datacite_user, self.datacite_pass, self.datacite_prefix,
                                                 self.button_draft_doi, self.button_doi_metadata,
                                                self.button_metadata_post])

    def on_click_button_metadata_post(self, b):

        # self.draftdoi = self.dataciteconn.draft_doi()

        # self.jsform.data.identifiers[0]["identifier"] = self.draftdoi
        
        data = self.jsform.data

        # Validate dictionary
        assert schema43.validate(data)

        # Generate DataCite XML from dictionary.
        # doc = schema43.tostring(data)

        # Set metadata for DOI
        # self.dataciteMDS.metadata_post(doc)

        self.draftdoi = self.dataciteconn.draft_doi(metadata = data)

        metadatadoi = self.dataciteconn.metadata_get(self.draftdoi)
        
        self.output_results.clear_output()
        
        self.tab.selected_index = 1
        
        with self.output_results:
            print(json.dumps(metadatadoi,indent = 4))

        
    
    def on_click_button_doi_metadata(self, b):
        metadatadoi = self.dataciteconn.metadata_get(self.draftdoi )
        
        # self.output_results.clear_output()
        
        self.tab.selected_index = 1
        
        with self.output_results:
            print(json.dumps(metadatadoi,indent = 4))

    def on_click_button_draft_doi(self, b):
        self.draftdoi = self.dataciteconn.draft_doi()
        
        # self.output_results.clear_output()
        
        self.tab.selected_index = 1
        
        with self.output_results:
            print(self.draftdoi)

            
    def observe_and_click(self):
        self.button_draft_doi.on_click(self.on_click_button_draft_doi)
        self.button_doi_metadata.on_click(self.on_click_button_doi_metadata)
        self.button_metadata_post.on_click(self.on_click_button_metadata_post)
        pass
    
    def run_app(self):
        app = widgets.AppLayout(header = self.header,
                 left_sidebar = self.lsidebar,
                 center = self.tab,
                 footer = None,
                 height='700px'
                 )
        display(app)
