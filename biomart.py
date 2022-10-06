#!/usr/bin/env python

import sys
from shlex import split as shlex_split
import requests
import pandas as pd

"""
to interact with martservice through www.biomart.org

Author: Xiao Jianfeng
last updated: 2013.08.21
              2022.10.06 - update to python3

http://www.biomart.org/martservice.html
	
 BioMart  	 MartService

(a) Querying BioMart

To submit a query using our webservices generate an XML document conforming to our Query XML syntax. This can be achieved simply by building up your query using MartView and hitting the XML button. This XML should be posted to http://www.biomart.org/martservice attached to a single parameter of query. For example you could either:

    save your query as Query.xml and then POST this using the webExample.pl script in our biomart-perl/scripts installation.
    submit using wget: wget -O results.txt 'http://www.biomart.org/biomart/martservice?query=MY_XML' replacing MY_XML with the XML obtained above, first removing any new lines.


(b) Retrieving Meta Data

    to retrieve registry information: http://www.biomart.org/biomart/martservice?type=registry
    to retrieve datasets available for a mart: http://www.biomart.org/biomart/martservice?type=datasets&mart=ensembl
    to retrieve attributes available for a dataset: http://www.biomart.org/biomart/martservice?type=attributes&dataset=oanatinus_gene_ensembl
    to retrieve filters available for a dataset: http://www.biomart.org/biomart/martservice?type=filters&dataset=oanatinus_gene_ensembl
    to retrieve configuration for a dataset: http://www.biomart.org/biomart/martservice?type=configuration&dataset=oanatinus_gene_ensembl


  	SOAP Access
The SOAP based access is functionally equivalent to the REST style access described above. For description on BioMart SOAP based Web Service (MartServiceSoap), see:

    MartServiceSoap Endpoint (for SOAP based access only): http://www.biomart.org/biomart/martsoap
    MartServiceSoap WSDL: http://www.biomart.org/biomart/martwsdl
    MartServiceSoap XSD: http://www.biomart.org/biomart/martxsd


For more information see the web services section of our documentation.
Page last updated: 05/10/2011 15:25:40

http://www.biomart.org/faqs.html is also worth reading. Many examples how to build queries are available here!!

added on 2012.7.5:
    if you want to query older version of ensembl, you need to use matview provided by ensembl.
    http://feb2012.archive.ensembl.org/biomart/martview/cb52d463c62bdb0ac8038b8202d4bf6e?VIRTUALSCHEMANAME=default&ATTRIBUTES=hsapiens_gene_ensembl.default.feature_page.ensembl_gene_id|hsapiens_gene_ensembl.default.feature_page.ensembl_transcript_id|hsapiens_gene_ensembl.default.feature_page.external_gene_id|hsapiens_gene_ensembl.default.feature_page.external_transcript_id|hsapiens_gene_ensembl.default.feature_page.go_id|hsapiens_gene_ensembl.default.feature_page.name_1006|hsapiens_gene_ensembl.default.feature_page.definition_1006|hsapiens_gene_ensembl.default.feature_page.go_linkage_type|hsapiens_gene_ensembl.default.feature_page.namespace_1003&FILTERS=hsapiens_gene_ensembl.default.filters.go_parent_term."GO:0006629"&VISIBLEPANEL=resultspanel
"""

DEBUG = False

mart_host = "http://www.biomart.org"
mart_url_prefix = "/biomart/martservice?"
mart_urls = {
    "biomart": "http://www.biomart.org/biomart/martservice?",
    "ensembl": "http://www.ensembl.org/biomart/martservice?",  # ensembl is more update and faster than biomart
    "ensgrch37": "http://grch37.ensembl.org/biomart/martservice",
    "ensemblv66": "http://feb2012.archive.ensembl.org/biomart/martservice?",
    "ensemblv67": "http://may2012.archive.ensembl.org/biomart/martservice?",
    "ensemblv68": "http://jul2012.archive.ensembl.org/biomart/martservice?",
    "ensemblv69": "http://Oct2012.archive.ensembl.org/biomart/martservice?",
    "ensemblv70": "http://jan2013.archive.ensembl.org/biomart/martservice?",
    "ensemblv71": "http://apr2013.archive.ensembl.org/biomart/martservice?",
    "ensemblv72": "http://jun2013.archive.ensembl.org/biomart/martservice?",
    "ensemblv73": "http://sep2013.archive.ensembl.org/biomart/martservice?",
    "ensemblv74": "http://dec2013.archive.ensembl.org/biomart/martservice?",
    "ensemblv75": "http://feb2014.archive.ensembl.org/biomart/martservice?",
    "ensemblv76": "http://aug2014.archive.ensembl.org/biomart/martservice?",
    "ensemblv77": "http://oct2014.archive.ensembl.org/biomart/martservice?",
    "ensemblv78": "http://dec2014.archive.ensembl.org/biomart/martservice?",
    "ensemblv79": "http://mar2015.archive.ensembl.org/biomart/martservice?",
    "ensemblv80": "http://may2015.archive.ensembl.org/biomart/martservice?",
    "ensemblv81": "http://jul2015.archive.ensembl.org/biomart/martservice?",
    "ensemblv82": "http://sep2015.archive.ensembl.org/biomart/martservice?",
    "ensemblv83": "http://dec2015.archive.ensembl.org/biomart/martservice?",
    "ensemblv84": "http://mar2016.archive.ensembl.org/biomart/martservice?",
    "ensemblv85": "http://jul2016.archive.ensembl.org/biomart/martviewice?",
    "ensemblv86": "http://oct2016.archive.ensembl.org/biomart/martservice?",
}

# -----------------------------------------------------------------
def build_query(dataset, attributes, filters=None, formatter="TSV"):
    """
    Only dataset, filters, and attributes are needed to build a query, while database is not needed.
    I guess this is because the dataset name is enough to identify itself.

    dataset: table name
    filters: should be a dict
    attributes: should be list

    formatter: TSV or FASTA
    """

    mart_query_dataset = """\t<Dataset name = "{}" interface = "default" >\n""".format(
        dataset
    )

    if formatter == "TSV":
        # Note: if header = "0" --> no header; header = "1" or "ture" --> with header
        # uniqueRows: "0" - don't remove duplicate lines; "1" - remove uplicatel ines.
        # limit = N could also be added
        mart_query_header = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE Query>
        <Query  virtualSchemaName = "default" formatter = "TSV" header = "1" uniqueRows = "1" count = "" datasetConfigVersion = "0.6" >\n"""
    elif formatter == "FASTA":
        mart_query_header = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE Query>
        <Query  virtualSchemaName = "default" formatter = "FASTA" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >\n"""
    else:
        raise Exception("Currently only 'TSV' and 'FASTA' are supported as formatter")

    mart_query_tail = "\t</Dataset>\n</Query>"

    if filters:  # filters may be None
        filter_buffer = []
        for k, v in list(filters.items()):
            if not isinstance(v, (list, tuple)):
                raise Exception("%s should be iterable" % v)
            if not isinstance(
                v, str
            ):  # v is a list or tuple of string, else, v is string
                v = ",".join(v)
            item_str = """\t\t<Filter name = "{}" value = "{}"/>\n""".format(k, v)
            filter_buffer.append(item_str)
        mart_query_filter = "".join(filter_buffer)
    else:
        mart_query_filter = ""

    if isinstance(attributes, str):  # if attributes is a single value, make it a list
        attributes = [attributes]
    mart_query_attributes = "".join(
        """\t\t<Attribute name = "{}" />\n""".format(s) for s in attributes
    )

    xml = (
        mart_query_header
        + mart_query_dataset
        + mart_query_filter
        + mart_query_attributes
        + mart_query_tail
    )

    return xml


def easy_response(params_dict, base_url=None, site=None, echo=False):
    """a helper function to post with requests and get response"""

    if site:
        base_url = mart_urls[site]
    else:
        if base_url is None:
            base_url = mart_urls["ensembl"]

    r = requests.post(base_url, data=params_dict)
    if DEBUG:
        sys.stderr.write("requests.post -\n{}: {}".format(base_url, params_dict))

    if DEBUG:
        sys.stderr.write("response -\n{}".format(r.headers))
    if r.ok:
        length = r.headers["Content-Length"] if "Content-Length" in r.headers else None

        sys.stderr.write("Start to download ")
        current_size, data = 0, []
        for buf in r.iter_content(1024 * 1024, decode_unicode=True):
            if buf:
                data.append(buf)
                current_size += len(buf)
                sys.stderr.write("\b- ")
        sys.stderr.write("\bdone.\n")

    else:
        raise Exception("Got error: %s" % r.error)

    if echo or DEBUG:
        print(data)

    return "".join(data)


# -----------------------------------------------------------------
class BioMart:
    def __init__(self, mart=None, dataset=None, timeout=1000, site="ensembl"):
        """it seems mart is not necessary to query biomart, dataset+[filters+]attributes is enough"""

        self.available_sites = list(mart_urls.keys())
        self.available_databases = None
        self.available_datasets = None

        if site:
            self.use_site(site)
        else:
            self.site = site

        if mart:
            self.use_mart(mart)
        else:
            self.mart = mart

        if dataset:
            self.use_dataset(dataset)
        else:
            self.dataset = dataset

        self.timeout = timeout

    def list_sites(self):

        return list(mart_urls.keys())

    def use_site(self, site):
        """available site: mart_urls.keys()"""

        if site and site in mart_urls:
            self.site = site
        else:
            raise Exception(
                "site {} is not valid.\n\t valid site: {}".format(
                    site, list(mart_urls.keys())
                )
            )

    # -------------------------------------------------

    def registry_information(self):
        """
        you don't need to use this. Use list_databases() instead
        """

        return self.list_databases()

    def list_databases(self, echo=True):
        """
                actually list all available databases

                "name" filed in retrieved information could be used to retrieve available datasets.

                Example:

        <MartRegistry>
          <MartURLLocation database="ensembl_mart_65" default="1" displayName="ENSEMBL GENES 65 (SANGER UK)" host="www.biomart.org" includeDatasets="" martUser="" name="ensembl" path="/biomart/martservice" port="80" serverVirtualSchema="default" visible="1" />
          <MartURLLocation database="snp_mart_65" default="0" displayName="ENSEMBL VARIATION 65 (SANGER UK)" host="www.biomart.org" includeDatasets="" martUser="" name="snp" path="/biomart/martservice" port="80" serverVirtualSchema="default" visible="1" />
          <MartURLLocation database="functional_genomics_mart_65" default="0" displayName="ENSEMBL REGULATION 65 (SANGER UK)" host="www.biomart.org" includeDatasets="" martUser="" name="functional_genomics" path="/biomart/martservice" port="80" serverVirtualSchema="default" visible="1" />
          ...
        </MartRegistry>

        database default            displayName             host includeDatasets martUser                   name                  path port serverVirtualSchema visible
        ENSEMBL_MART_SEQUENCE          sequence_mart_87                       Sequence  www.ensembl.org                           ENSEMBL_MART_SEQUENCE  /biomart/martservice   80             default
        ENSEMBL_MART_VEGA                  vega_mart_87                        Vega 67  www.ensembl.org                               ENSEMBL_MART_VEGA  /biomart/martservice   80             default       1
        ENSEMBL_MART_ONTOLOGY          ontology_mart_87                       Ontology  www.ensembl.org                           ENSEMBL_MART_ONTOLOGY  /biomart/martservice   80             default
        ENSEMBL_MART_FUNCGEN         regulation_mart_87          Ensembl Regulation 87  www.ensembl.org                            ENSEMBL_MART_FUNCGEN  /biomart/martservice   80             default       1
        ENSEMBL_MART_MOUSE                mouse_mart_87               Mouse strains 87  www.ensembl.org                              ENSEMBL_MART_MOUSE  /biomart/martservice   80             default       1
        ENSEMBL_MART_GENOMIC   genomic_features_mart_87            Genomic features 87  www.ensembl.org                            ENSEMBL_MART_GENOMIC  /biomart/martservice   80             default
        ENSEMBL_MART_SNP                    snp_mart_87           Ensembl Variation 87  www.ensembl.org                                ENSEMBL_MART_SNP  /biomart/martservice   80             default       1
        ENSEMBL_MART_ENSEMBL            ensembl_mart_87       1       Ensembl Genes 87  www.ensembl.org                            ENSEMBL_MART_ENSEMBL  /biomart/martservice   80             default       1"""

        params_dict = {"type": "registry"}

        data = easy_response(params_dict, site=self.site, echo=False)

        db_dict = {}
        # column 'name' should be used by self.use_database()
        for ln in data.strip().splitlines():
            ln_dict = dict(item.split("=") for item in shlex_split(ln) if "=" in item)
            if "name" in ln_dict:
                db = ln_dict["name"]
                db_dict[db] = ln_dict
        databases = pd.DataFrame(list(db_dict.values()), index=list(db_dict.keys()))
        if echo:
            sys.stderr.write(databases.to_string())

        return databases

    def use_mart(self, mart):
        """set the value of mart
        This method is the same with use_database"""
        self.use_database(mart)

    def use_database(self, database):

        # if self.available_databases is not set, set it first
        if self.available_databases is None:
            self.available_databases = list(self.list_databases(echo=False)["name"])

        if database and database in self.available_databases:
            self.mart = database
        else:
            raise Exception(
                "database/mart {} is not valid.\n\t valid databases: {}".format(
                    database, self.available_databases
                )
            )

    # -------------------------------------------------

    def list_datasets(self, mart=None, echo=True):
        """
        TableSet	oanatinus_gene_ensembl	Ornithorhynchus anatinus genes (OANA5)	1	OANA5	200	50000	default	2011-09-07 22:26:09
        TableSet	tguttata_gene_ensembl	Taeniopygia guttata genes (taeGut3.2.4)	1	taeGut3.2.4	200	50000	default	2011-09-07 22:26:36
        TableSet	cporcellus_gene_ensembl	Cavia porcellus genes (cavPor3)	1	cavPor3	200	50000	default	2011-09-07 22:27:40
        (......)

        The second column could be used in self.list_attributes() and self.list_filters() to retrieve available attributes and filters for a given dataset."""

        mart = mart if mart else self.mart
        if mart is None:
            raise Exception(
                "self.mart is None, either set self.mart first, or provide a 'mart=' here."
            )
        if echo:
            sys.stderr.write("Mart being used is: {}\n".format(mart))

        params_dict = {"type": "datasets", "mart": mart}
        data = easy_response(params_dict, site=self.site, echo=False)

        # parse the output to make it more readable
        data2 = [ln.split("\t") for ln in data.strip().split("\n") if ln.strip()]

        datasets = pd.DataFrame(
            data2,
            columns=[
                "type",
                "name",
                "displayName",
                "visible",
                "version",
                "sth2",
                "sth3",
                "default",
                "modified",
            ],
        )
        if echo:
            sys.stderr.write(datasets.to_string())

        return datasets

    def use_dataset(self, dataset):

        # since "database" or "mart" infor is not needed buy a query(), it is OK to not provide "database/mart"

        # # if self.available_datasets is not set, set it first
        # if self.mart is None:
        #     raise Exception("self.mart is not set.")
        # if self.available_datasets is None:
        #     self.available_datasets = list(self.list_datasets(echo=False)['name'])

        # if dataset and dataset in self.available_datasets:
        #     self.dataset = dataset
        # else:
        #     raise Exception("dataset {} is not valid.\n\t valid datasets: {}".format(dataset, self.available_datasets))

        self.dataset = dataset

    # -------------------------------------------------

    def list_attributes(self, dataset=None):
        """
        To retrieve available attributes for a given dataset.

        dataset is a valid dataset, for example: hsapiens_gene_ensembl, oanatinus_gene_ensembl, tguttata_gene_ensembl
        dataset could be retrived by self.list_datasets()
        """

        dataset = dataset if dataset else self.dataset
        if dataset is None:
            raise Exception(
                "dataset in list_attributes() and self.dataset couldn't be all None"
            )
        print("Dataset being used is: ", dataset)

        params_dict = {"type": "attributes", "dataset": dataset}
        data = easy_response(params_dict, site=self.site, echo=False)

        # parse the output to make it more readable
        data2 = [ln.split("\t") for ln in data.strip().split("\n")]
        attributes = pd.DataFrame(data2)

        sys.stderr.write(attributes.to_string())

        return attributes

    def list_filters(self, dataset=None):
        """
        To retrieve available filters for a given dataset.
        """

        dataset = dataset if dataset else self.dataset
        if dataset is None:
            raise Exception(
                "dataset in list_filters() and self.dataset couldn't be all None"
            )
        print("Dataset being used is: ", dataset)

        params_dict = {"type": "filters", "dataset": dataset}
        data = easy_response(params_dict, site=self.site, echo=False)

        # parse the output to make it more readable
        data2 = [ln.split("\t") for ln in data.strip().split("\n")]
        filters = pd.DataFrame(data2)

        sys.stderr.write(filters.to_string())

        return filters

    def configuration(self, dataset=None):
        """
        To get configuration for a dataset.
        """

        dataset = dataset if dataset else self.dataset
        if dataset is None:
            raise Exception(
                "dataset in configuration() and self.dataset couldn't be all None"
            )
        print("Dataset being used is: ", dataset)

        params_dict = {"type": "configuration", "dataset": dataset}

        return easy_response(params_dict, site=self.site, echo=True)

    def xml_query(self, xml=None):
        '''
        >>> BioMart(site="ensembl").xml_query(xml="""<!DOCTYPE Query><Query client="true" processor="TSV" limit="2" header="1"><Dataset name="hsapiens_gene_ensembl" config="gene_ensembl_config"><Filter name="chromosome_name" value="1" filter_list=""/><Attribute name="ensembl_gene_id"/><Attribute name="ensembl_transcript_id"/></Dataset></Query>""")
        '''

        if xml is None:
            raise Exception("not valid input for xml_query")

        params_dict = {"query": xml}

        return easy_response(params_dict, site=self.site)

    def query(
        self, attributes=None, xml=None, filters=None, dataset=None, return_raw=False
    ):
        """
        example:
            filters: {"affy_hg_u133a_2": ("202763_at","209310_s_at","207500_at")}
            attributes: ["ensembl_gene_id", "ensembl_transcript_id", "affy_hg_u133a_2"]
            dataset: "hsapiens_gene_ensembl"

        Note: "mart" or "database" info is not needed by query().
        """

        if xml is None:  # query with xml
            dataset = dataset if dataset else self.dataset
            if dataset is None:
                raise Exception(
                    "dataset in query() and self.dataset couldn't be all None"
                )

            xml = build_query(dataset=dataset, attributes=attributes, filters=filters)

        params_dict = {"query": xml}
        print(params_dict)
        data = easy_response(params_dict, site=self.site)

        if return_raw:
            return data
        else:
            # TODO: check the output format as this only works for TSV format with header
            data2 = [ln.split("\t") for ln in data.strip().split("\n")]
            colnames = data2[0]
            results = pd.DataFrame(data2[1:], columns=colnames)

            return results

    def get_BM(self, *args, **kwds):
        return self.query(*args, **kwds)


# -----------------------------------------------------------------------


def test_query():
    # mart_query_database = 'ensembl'  # not needed, as the dataset name itself is enough to identify itself.
    # could be one dataset or more, how to explain multiple datasets remains to be determined
    mart_query_dataset = "hsapiens_gene_ensembl"
    mart_query_filters = {"chromosome_name": "Y"}
    mart_query_attributes = [
        "ensembl_gene_id",
        "ensembl_transcript_id",
        "hgnc_id",
        "hgnc_transcript_name",
        "hgnc_symbol",
    ]

    xml = build_query(
        dataset=mart_query_dataset,
        attributes=mart_query_attributes,
        filters=mart_query_filters,
    )
    print(xml)
    params_dict = {"query": xml}

    return easy_response(params_dict)


def test():

    mart_query_example = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >
                    
    <Dataset name = "hsapiens_gene_ensembl" interface = "default" >
            <Filter name = "ensembl_gene_id" value = "ENSG00000162367,ENSG00000187048"/>
            <Attribute name = "hgnc_symbol" />
            <Attribute name = "affy_hc_g110" />
            <Attribute name = "ensembl_gene_id" />
            <Attribute name = "entrezgene" />
            <Attribute name = "ensembl_transcript_id" />
    </Dataset>
</Query>"""
    mart_example_output = """ HGNC symbol 	Affy HC G110 	Ensembl Gene ID 	EntrezGene ID 	Ensembl Transcript ID
TAL1 	560_s_at 	ENSG00000162367 	6886 	ENST00000371884
TAL1 	560_s_at 	ENSG00000162367 	6886 	ENST00000294339
TAL1 		ENSG00000162367 	6886 	ENST00000459729
TAL1 		ENSG00000162367 	6886 	ENST00000464796
TAL1 		ENSG00000162367 	6886 	ENST00000481091
TAL1 		ENSG00000162367 	6886 	ENST00000465912
TAL1 	560_s_at 	ENSG00000162367 	6886 	ENST00000371883
CYP4A11 	1391_s_at 	ENSG00000187048 	1579 	ENST00000310638
CYP4A11 	1391_s_at 	ENSG00000187048 	1579 	ENST00000475477
CYP4A11 	1391_s_at 	ENSG00000187048 	1579 	ENST00000462347
"""

    params_dict = {"query": mart_query_example}

    return easy_response(params_dict)


def test_list():
    """
        filters: affy_hg_u133a_2: ("202763_at","209310_s_at","207500_at")
        attributes: ["ensembl_gene_id", "ensembl_transcript_id", "affy_hg_u133a_2"]
        dataset: hsapiens_gene_ensembl

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE Query>
    <Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "0" count = "" datasetConfigVersion = "0.6" >

        <Dataset name = "hsapiens_gene_ensembl" interface = "default" >
                <Filter name = "affy_hg_u133a_2" value = "202763_at,209310_s_at,207500_at"/>
                <Attribute name = "ensembl_gene_id" />
                <Attribute name = "ensembl_transcript_id" />
                <Attribute name = "affy_hg_u133_plus_2" />
        </Dataset>
    </Query>

    Ensembl Gene ID 	Ensembl Transcript ID 	Affy HG U133-PLUS-2 probeset
    ENSG00000196954 	ENST00000525116 	209310_s_at
    ENSG00000196954 	ENST00000444739 	209310_s_at
    ENSG00000196954 	ENST00000393150 	209310_s_at
    ENSG00000196954 	ENST00000529565 	213596_at
    ENSG00000196954 	ENST00000529565 	209310_s_at
    ENSG00000196954 	ENST00000533730 	209310_s_at
    ENSG00000196954 	ENST00000534356 	209310_s_at
    ENSG00000196954 	ENST00000355546 	209310_s_at
    ENSG00000137757 	ENST00000438448 	207500_at
    ENSG00000137757 	ENST00000260315 	207500_at"""

    attributes = [
        "ensembl_gene_id",
        "ensembl_transcript_id",
        "affy_hg_u133_plus_2",
        "hgnc_symbol",
        "chromosome_name",
        "start_position",
        "end_position",
    ]
    filters = {"affy_hg_u133_plus_2": ("202763_at", "209310_s_at", "207500_at")}
    dataset = "hsapiens_gene_ensembl"

    results = BioMart().query(attributes=attributes, filters=filters, dataset=dataset)
    print(results)

    return results


def test_allinone():
    BioMart(mart="ENSEMBL_MART_ENSEMBL", dataset="hsapiens_gene_ensembl").query(
        filters={"hgnc_symbol": ["EGFR", "KRAS", "NRAS", "BRAF"]},
        attributes=[
            "ensembl_gene_id",
            "ensembl_transcript_id",
            "external_gene_name",
            "hgnc_symbol",
            "start_position",
            "end_position",
            "band",
            "refseq_mrna",
            "refseq_peptide",
        ],
    )


def test_allinone2():
    BioMart().query(
        dataset="hsapiens_gene_ensembl",
        filters={"hgnc_symbol": ["EGFR", "KRAS", "NRAS", "BRAF"]},
        attributes=[
            "ensembl_gene_id",
            "ensembl_transcript_id",
            "external_gene_name",
            "hgnc_symbol",
            "start_position",
            "end_position",
            "band",
            "refseq_mrna",
            "refseq_peptide",
        ],
    )


# TODO:
# 1) to write some examples similar with biomaRt in bioconductor.
# 2) clean the parameter list of all functions

# -----------------------------------------------------------------------
# main
# -----------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    # print BioMart().test()
    # print BioMart().test_query()
    # raw_input("look")

    parser = argparse.ArgumentParser(
        description="query biomart from ensembl or biomart.org."
    )
    parser.add_argument(
        "-x", "--xml", dest="xml", default=None, help="query string in xml format"
    )
    parser.add_argument(
        "-d", "--dataset", dest="dataset", default=None, help="dataset to query"
    )
    parser.add_argument(
        "-a",
        "--attributes",
        dest="attributes",
        default=None,
        help="attributes of query",
    )
    parser.add_argument(
        "-f", "--filters", dest="filters", default=None, help="filter[s] for query"
    )
    parser.add_argument(
        "-s",
        "--site",
        dest="site",
        default="ensembl",
        help=("site used for query, current available: %s" % list(mart_urls.keys())),
    )

    # parser.add_argument('terms', nargs='*', help="GO terms to be visualized")

    args = parser.parse_args()

    bm = BioMart()
    if args.site is not None:
        bm.use_site(args.site)

    if args.xml is not None:
        if args.xml == "-":
            xml = sys.stdin.read()
        else:
            xml = open(args.xml).read()
        sys.stdout.write(bm.query(xml=xml, return_raw=True))
    else:  # args.xml is None, will build query from dataset, attributes and filters.
        pass
    # TODO: to be continued

    # TODO: make a few practial examples, eg. get refseq NM id for a gene symbol.

    BioMart(mart="ENSEMBL_MART_ENSEMBL", dataset="hsapiens_gene_ensembl").query(
        filters={"hgnc_symbol": ["EGFR", "KRAS", "NRAS", "BRAF"]},
        attributes=[
            "ensembl_gene_id",
            "ensembl_transcript_id",
            "external_gene_name",
            "hgnc_symbol",
            "start_position",
            "end_position",
            "band",
            "refseq_mrna",
            "refseq_peptide",
        ],
    )

    result = BioMart().query(
        dataset="hsapiens_gene_ensembl",
        filters={"hgnc_symbol": ["EGFR", "KRAS", "NRAS", "BRAF"]},
        attributes=[
            "ensembl_gene_id",
            "ensembl_transcript_id",
            "external_gene_name",
            "hgnc_symbol",
            "start_position",
            "end_position",
            "band",
            "refseq_mrna",
            "refseq_peptide",
        ],
    )
    sys.stout.write(result)
