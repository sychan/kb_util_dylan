/*
** A KBase module: kb_util_dylan
**
** This module contains basic utilities
*/

module kb_util_dylan {

    /* 
    ** The workspace object refs are of form:
    **
    **    objects = ws.get_objects([{'ref': params['workspace_id']+'/'+params['obj_name']}])
    **
    ** "ref" means the entire name combining the workspace id and the object name
    ** "id" is a numerical identifier of the workspace or object, and should just be used for workspace
    ** "name" is a string identifier of a workspace or object.  This is received from Narrative.
    */
    typedef string workspace_name;
    typedef string sequence;
    typedef string data_obj_name;
    typedef string data_obj_ref;


    /* KButil_Insert_SingleEndLibrary()
    **
    ** Method for Inserting a textarea field with FASTA or FASTQ into a SingleEndLibrary object and importing into SHOCK and WS
    */
    /*
    typedef structure {
        workspace_name workspace_name;
	sequence       input_sequence;
        data_obj_name  output_name;
    } KButil_Insert_SingleEndLibrary_Params;

    typedef structure {
	data_obj_name report_name;
	data_obj_ref  report_ref;
    */
/*       data_obj_ref  output_filtered_ref;
*
*        int n_initial_seqs;
*        int n_seqs_matched;
*        int n_seqs_notmatched;
*/
    /*
    } KButil_Insert_SingleEndLibrary_Output;
    */
    /*funcdef KButil_Insert_SingleEndLibrary (KButil_Insert_SingleEndLibrary_Params params)  returns (KButil_Insert_SingleEndLibrary_Output) authentication required;
    */
	

    /* KButil_FASTQ_to_FASTA()
    **
    ** Method for Converting a FASTQ SingleEndLibrary to a FASTA SingleEndLibrary
    */
    typedef structure {
        workspace_name workspace_name;
	data_obj_name  input_name;
        data_obj_name  output_name;
    } KButil_FASTQ_to_FASTA_Params;

    typedef structure {
	data_obj_name report_name;
	data_obj_ref  report_ref;
/*       data_obj_ref  output_filtered_ref;
*
*        int n_initial_seqs;
*        int n_seqs_matched;
*        int n_seqs_notmatched;
*/
    } KButil_FASTQ_to_FASTA_Output;
	
    funcdef KButil_FASTQ_to_FASTA (KButil_FASTQ_to_FASTA_Params params)  returns (KButil_FASTQ_to_FASTA_Output) authentication required;


    /* KButil_Merge_FeatureSet_Collection()
    **
    **  Method for merging FeatureSets
    */
    typedef structure {
        workspace_name workspace_name;
	data_obj_name  input_names;
        data_obj_name  output_name;
	string         desc;
    } KButil_Merge_FeatureSet_Collection_Params;

    typedef structure {
	data_obj_name report_name;
	data_obj_ref  report_ref;
    } KButil_Merge_FeatureSet_Collection_Output;

    funcdef KButil_Merge_FeatureSet_Collection (KButil_Merge_FeatureSet_Collection_Params params)  returns (KButil_Merge_FeatureSet_Collection_Output) authentication required;


    /* KButil_Merge_GenomeSets()
    **
    **  Method for merging GenomeSets
    */
    typedef structure {
        workspace_name workspace_name;
	data_obj_name  input_names;
        data_obj_name  output_name;
	string         desc;
    } KButil_Merge_GenomeSets_Params;

    typedef structure {
	data_obj_name report_name;
	data_obj_ref  report_ref;
    } KButil_Merge_GenomeSets_Output;

    funcdef KButil_Merge_GenomeSets (KButil_Merge_GenomeSets_Params params)  returns (KButil_Merge_GenomeSets_Output) authentication required;


    /* KButil_Build_GenomeSet()
    **
    **  Method for creating a GenomeSet
    */
    typedef structure {
        workspace_name workspace_name;
	data_obj_name  input_names;
        data_obj_name  output_name;
	string         desc;
    } KButil_Build_GenomeSet_Params;

    typedef structure {
	data_obj_name report_name;
	data_obj_ref  report_ref;
    } KButil_Build_GenomeSet_Output;

    funcdef KButil_Build_GenomeSet (KButil_Build_GenomeSet_Params params)  returns (KButil_Build_GenomeSet_Output) authentication required;


    /* KButil_Build_GenomeSet_from_FeatureSet()
    **
    **  Method for obtaining a GenomeSet from a FeatureSet
    */
    typedef structure {
        workspace_name workspace_name;
	data_obj_name  input_name;
        data_obj_name  output_name;
	string         desc;
    } KButil_Build_GenomeSet_from_FeatureSet_Params;

    typedef structure {
	data_obj_name report_name;
	data_obj_ref  report_ref;
    } KButil_Build_GenomeSet_from_FeatureSet_Output;

    funcdef KButil_Build_GenomeSet_from_FeatureSet (KButil_Build_GenomeSet_from_FeatureSet_Params params)  returns (KButil_Build_GenomeSet_from_FeatureSet_Output) authentication required;


    /* KButil_Add_Genomes_to_GenomeSet()
    **
    **  Method for adding a Genome to a GenomeSet
    */
    typedef structure {
        workspace_name workspace_name;
	data_obj_name  input_genome_names;
        data_obj_name  input_genomeset_name;
        data_obj_name  output_name;
	string         desc;
    } KButil_Add_Genomes_to_GenomeSet_Params;

    typedef structure {
	data_obj_name report_name;
	data_obj_ref  report_ref;
    } KButil_Add_Genomes_to_GenomeSet_Output;

    funcdef KButil_Add_Genomes_to_GenomeSet (KButil_Add_Genomes_to_GenomeSet_Params params)  returns (KButil_Add_Genomes_to_GenomeSet_Output) authentication required;


    /* KButil_Concat_MSAs()
    **
    **  Method for Concatenating MSAs into a combined MSA
    */
    typedef structure {
        workspace_name workspace_name;
	data_obj_name  input_names;
        data_obj_name  output_name;
	string         desc;
	int            blanks_flag;  /* actually bool */
    } KButil_Concat_MSAs_Params;

    typedef structure {
	data_obj_name report_name;
	data_obj_ref  report_ref;
    } KButil_Concat_MSAs_Output;

    funcdef KButil_Concat_MSAs (KButil_Concat_MSAs_Params params)  returns (KButil_Concat_MSAs_Output) authentication required;


    /* KButil_Split_Reads()
    **
    **  Method for spliting a ReadsLibrary into evenly sized ReadsLibraries
    */
    typedef structure {
        workspace_name workspace_name;
	data_obj_name  input_name;  /* Reads Libraries */
        data_obj_name  output_name;  /* ReadsSet */
	string         desc;
    } KButil_Split_Reads_Params;

    typedef structure {
	data_obj_name report_name;
	data_obj_ref  report_ref;
    } KButil_Split_Reads_Output;

    funcdef KButil_Split_Reads (KButil_Split_Reads_Params params)  returns (KButil_Split_Reads_Output) authentication required;

};

