import unittest
import os
import json
import time
import requests
import shutil

from os import environ
from ConfigParser import ConfigParser
from requests_toolbelt import MultipartEncoder
from pprint import pprint

from Workspace.WorkspaceClient import Workspace as workspaceService
from biokbase.AbstractHandle.Client import AbstractHandle as HandleService
from kb_util_dylan.kb_util_dylanImpl import kb_util_dylan
from ReadsUtils.ReadsUtilsClient import ReadsUtils
from AssemblyUtil.AssemblyUtilClient import AssemblyUtil


class kb_util_dylanTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        cls.token = token
        cls.ctx = {'token': token, 'provenance': [{'service': 'kb_util_dylan',
            'method': 'please_never_use_it_in_production', 'method_params': []}],
            'authenticated': 1}
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_util_dylan'):
            print(nameval[0] + '=' + nameval[1])
            cls.cfg[nameval[0]] = nameval[1]
        cls.wsURL = cls.cfg['workspace-url']
        cls.shockURL = cls.cfg['shock-url']
        cls.handleURL = cls.cfg['handle-service-url']
        cls.serviceWizardURL = cls.cfg['service-wizard-url']
        cls.callbackURL = os.environ['SDK_CALLBACK_URL']
        cls.wsClient = workspaceService(cls.wsURL, token=token)
        cls.serviceImpl = kb_util_dylan(cls.cfg)
        cls.scratch = os.path.abspath(cls.cfg['scratch'])
        if not os.path.exists(cls.scratch):
            os.makedirs(cls.scratch)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')
        if hasattr(cls, 'shock_ids'):
            for shock_id in cls.shock_ids:
                print('Deleting SHOCK node: '+str(shock_id))
                cls.delete_shock_node(shock_id)

    @classmethod
    def delete_shock_node(cls, node_id):
        header = {'Authorization': 'Oauth {0}'.format(cls.token)}
        requests.delete(cls.shockURL + '/node/' + node_id, headers=header,
                        allow_redirects=True)
        print('Deleted shock node ' + node_id)

    def getWsClient(self):
        return self.__class__.wsClient

    def getWsName(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_kb_util_dylan_" + str(suffix)
        ret = self.getWsClient().create_workspace({'workspace': wsName})
        self.__class__.wsName = wsName
        return wsName

    def getImpl(self):
        return self.__class__.serviceImpl

    def getContext(self):
        return self.__class__.ctx


    # call this method to get the WS object info of a Single End Library (will
    # upload the example data if this is the first time the method is called during tests)
    def getSingleEndLibInfo(self, read_lib_basename, lib_i=0):
        if hasattr(self.__class__, 'singleEndLibInfo_list'):
            try:
                info = self.__class__.singleEndLibInfo_list[lib_i]
                name = self.__class__.singleEndLibName_list[lib_i]
                if info != None:
                    if name != read_lib_basename:
                        self.__class__.singleEndLibInfo_list[lib_i] = None
                        self.__class__.singleEndLibName_list[lib_i] = None
                    else:
                        return info
            except:
                pass

        # 1) upload files to shock
        shared_dir = "/kb/module/work/tmp"
        forward_data_file = 'data/'+read_lib_basename+'.fwd.fq'
        forward_file = os.path.join(shared_dir, os.path.basename(forward_data_file))
        shutil.copy(forward_data_file, forward_file)

        ru = ReadsUtils(os.environ['SDK_CALLBACK_URL'])
        single_end_ref = ru.upload_reads({'fwd_file': forward_file,
                                          'sequencing_tech': 'artificial reads',
                                          'wsname': self.getWsName(),
                                          'name': 'test-'+str(lib_i)+'.se.reads'})['obj_ref']

        new_obj_info = self.getWsClient().get_object_info_new({'objects': [{'ref': single_end_ref}]})[0]

        # store it
        if not hasattr(self.__class__, 'singleEndLibInfo_list'):
            self.__class__.singleEndLibInfo_list = []
            self.__class__.singleEndLibName_list = []
        for i in range(lib_i+1):
            try:
                assigned = self.__class__.singleEndLibInfo_list[i]
            except:
                self.__class__.singleEndLibInfo_list.append(None)
                self.__class__.singleEndLibName_list.append(None)

        self.__class__.singleEndLibInfo_list[lib_i] = new_obj_info
        self.__class__.singleEndLibName_list[lib_i] = read_lib_basename
        return new_obj_info


    # call this method to get the WS object info of a Paired End Library (will
    # upload the example data if this is the first time the method is called during tests)
    def getPairedEndLibInfo(self, read_lib_basename, lib_i=0):
        if hasattr(self.__class__, 'pairedEndLibInfo_list'):
            try:
                info = self.__class__.pairedEndLibInfo_list[lib_i]
                name = self.__class__.pairedEndLibName_list[lib_i]
                if info != None:
                    if name != read_lib_basename:
                        self.__class__.pairedEndLibInfo_list[lib_i] = None
                        self.__class__.pairedEndLibName_list[lib_i] = None
                    else:
                        return info
            except:
                pass

        # 1) upload files to shock
        shared_dir = "/kb/module/work/tmp"
        forward_data_file = 'data/'+read_lib_basename+'.fwd.fq'
        forward_file = os.path.join(shared_dir, os.path.basename(forward_data_file))
        shutil.copy(forward_data_file, forward_file)
        reverse_data_file = 'data/'+read_lib_basename+'.rev.fq'
        reverse_file = os.path.join(shared_dir, os.path.basename(reverse_data_file))
        shutil.copy(reverse_data_file, reverse_file)

        ru = ReadsUtils(os.environ['SDK_CALLBACK_URL'])
        paired_end_ref = ru.upload_reads({'fwd_file': forward_file, 'rev_file': reverse_file,
                                          'sequencing_tech': 'artificial reads',
                                          'interleaved': 0, 'wsname': self.getWsName(),
                                          'name': 'test-'+str(lib_i)+'.pe.reads'})['obj_ref']

        new_obj_info = self.getWsClient().get_object_info_new({'objects': [{'ref': paired_end_ref}]})[0]

        # store it
        if not hasattr(self.__class__, 'pairedEndLibInfo_list'):
            self.__class__.pairedEndLibInfo_list = []
            self.__class__.pairedEndLibName_list = []
        for i in range(lib_i+1):
            try:
                assigned = self.__class__.pairedEndLibInfo_list[i]
            except:
                self.__class__.pairedEndLibInfo_list.append(None)
                self.__class__.pairedEndLibName_list.append(None)

        self.__class__.pairedEndLibInfo_list[lib_i] = new_obj_info
        self.__class__.pairedEndLibName_list[lib_i] = read_lib_basename
        return new_obj_info


    # call this method to get the WS object info of a Single End Library Set (will
    # upload the example data if this is the first time the method is called during tests)
    def getSingleEndLib_SetInfo(self, read_libs_basename_list, refresh=False):
        if hasattr(self.__class__, 'singleEndLib_SetInfo'):
            try:
                info = self.__class__.singleEndLib_SetInfo
                if info != None:
                    if refresh:
                        self.__class__.singleEndLib_SetInfo = None
                    else:
                        return info
            except:
                pass

        # build items and save each SingleEndLib
        items = []
        for lib_i,read_lib_basename in enumerate (read_libs_basename_list):
            label    = read_lib_basename
            lib_info = self.getSingleEndLibInfo (read_lib_basename, lib_i)
            lib_ref  = str(lib_info[6])+'/'+str(lib_info[0])+'/'+str(lib_info[4])
            print ("LIB_REF["+str(lib_i)+"]: "+lib_ref+" "+read_lib_basename)  # DEBUG

            items.append({'ref': lib_ref,
                          'label': label
                          #'data_attachment': ,
                          #'info':
                         })

        # save readsset
        desc = 'test ReadsSet'
        readsSet_obj = { 'description': desc,
                         'items': items
                       }
        name = 'TEST_READSET'

        new_obj_set_info = self.wsClient.save_objects({
                        'workspace':self.getWsName(),
                        'objects':[
                            {
                                'type':'KBaseSets.ReadsSet',
                                'data':readsSet_obj,
                                'name':name,
                                'meta':{},
                                'provenance':[
                                    {
                                        'service':'kb_util_dylan',
                                        'method':'test_kb_util_dylan'
                                    }
                                ]
                            }]
                        })[0]

        # store it
        self.__class__.singleEndLib_SetInfo = new_obj_set_info
        return new_obj_set_info


    # call this method to get the WS object info of a Paired End Library Set (will
    # upload the example data if this is the first time the method is called during tests)
    def getPairedEndLib_SetInfo(self, read_libs_basename_list, refresh=False):
        if hasattr(self.__class__, 'pairedEndLib_SetInfo'):
            try:
                info = self.__class__.pairedEndLib_SetInfo
                if info != None:
                    if refresh:
                        self.__class__.pairedEndLib_SetInfo = None
                    else:
                        return info
            except:
                pass

        # build items and save each PairedEndLib
        items = []
        for lib_i,read_lib_basename in enumerate (read_libs_basename_list):
            label    = read_lib_basename
            lib_info = self.getPairedEndLibInfo (read_lib_basename, lib_i)
            lib_ref  = str(lib_info[6])+'/'+str(lib_info[0])+'/'+str(lib_info[4])
            lib_type = str(lib_info[2])
            print ("LIB_REF["+str(lib_i)+"]: "+lib_ref+" "+read_lib_basename)  # DEBUG
            print ("LIB_TYPE["+str(lib_i)+"]: "+lib_type+" "+read_lib_basename)  # DEBUG

            items.append({'ref': lib_ref,
                          'label': label
                          #'data_attachment': ,
                          #'info':
                         })

        # save readsset
        desc = 'test ReadsSet'
        readsSet_obj = { 'description': desc,
                         'items': items
                       }
        name = 'TEST_READSET'

        new_obj_set_info = self.wsClient.save_objects({
                        'workspace':self.getWsName(),
                        'objects':[
                            {
                                'type':'KBaseSets.ReadsSet',
                                'data':readsSet_obj,
                                'name':name,
                                'meta':{},
                                'provenance':[
                                    {
                                        'service':'kb_util_dylan',
                                        'method':'test_kb_util_dylan'
                                    }
                                ]
                            }]
                        })[0]

        # store it
        self.__class__.pairedEndLib_SetInfo = new_obj_set_info
        return new_obj_set_info


    ##############
    # UNIT TESTS #
    ##############


    #### test_KButil_FASTQ_to_FASTA():
    ##
    def test_KButil_FASTQ_to_FASTA (self):
        method = 'KButil_FASTQ_to_FASTA'

        print ("\n\nRUNNING: test_KButil_FASTQ_to_FASTA()")
        print ("=====================================\n\n")

        # figure out where the test data lives
        se_lib_info = self.getSingleEndLibInfo('test_quick')
        pprint(se_lib_info)

        # run method
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_ref': str(se_lib_info[6])+'/'+str(se_lib_info[0]),
            'output_name': base_output_name
        }
        result = self.getImpl().KButil_FASTQ_to_FASTA(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseFile.SingleEndLibrary'
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':se_lib_info[7] + '/' + output_name}]})
        self.assertEqual(len(info_list),1)
        readsLib_info = info_list[0]
        self.assertEqual(readsLib_info[1],output_name)
        self.assertEqual(readsLib_info[2].split('-')[0],output_type)
        pass


    #### test_KButil_Merge_FeatureSet_Collection():
    ##
    def test_KButil_Merge_FeatureSet_Collection (self):
        method = 'KButil_Merge_FeatureSet_Collection'

        print ("\n\nRUNNING: test_KButil_Merge_FeatureSet_Collection()")
        print ("==================================================\n\n")

        # input_data
        reference_prok_genomes_WS = 'ReferenceDataManager'  # PROD and CI
        genome_ref_1 = reference_prok_genomes_WS+'/GCF_001566335.1/1'  # E. coli K-12 MG1655
        genome_ref_2 = reference_prok_genomes_WS+'/GCF_000021385.1/1'  # D. vulgaris str. 'Miyazaki F'
        genome_ref_3 = reference_prok_genomes_WS+'/GCF_900129775.1/1'  # Halobaculum gomorrense (16 contigs)
        genome_id_feature_id_delim = '.f:'
        feature_id_1 = 'AWN69_RS07145'
        feature_id_2 = 'DVMF_RS00005'
        feature_id_3 = 'BUE16_RS15805'

        # featureSet 1
        featureSet_obj_1 = { 'description': 'test featureSet 1',
                             'element_ordering': [
                                 feature_id_1,
                                 feature_id_2
                             ],
                             'elements': { 
                                 feature_id_1: [genome_ref_1],
                                 feature_id_2: [genome_ref_2]
                             }
                         }
        provenance = [{}]
        featureSet_info = self.getWsClient().save_objects({
            'workspace': self.getWsName(), 
            'objects': [
                {
                    'type': 'KBaseCollections.FeatureSet',
                    'data': featureSet_obj_1,
                    'name': 'test_featureSet_1',
                    'meta': {},
                    'provenance': provenance
                }
            ]})[0]

        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        featureSet_ref_1 = str(featureSet_info[WSID_I])+'/'+str(featureSet_info[OBJID_I])+'/'+str(featureSet_info[VERSION_I])

        # featureSet 2
        featureSet_obj_2 = { 'description': 'test featureSet 2',
                             'element_ordering': [
                                 feature_id_3
                             ],
                             'elements': { 
                                 feature_id_3: [genome_ref_3]
                             }
                         }
        provenance = [{}]
        featureSet_info = self.getWsClient().save_objects({
            'workspace': self.getWsName(), 
            'objects': [
                {
                    'type': 'KBaseCollections.FeatureSet',
                    'data': featureSet_obj_2,
                    'name': 'test_featureSet_2',
                    'meta': {},
                    'provenance': provenance
                }
            ]})[0]

        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        featureSet_ref_2 = str(featureSet_info[WSID_I])+'/'+str(featureSet_info[OBJID_I])+'/'+str(featureSet_info[VERSION_I])

        # run method
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': [featureSet_ref_1, featureSet_ref_2],
            'output_name': base_output_name,
            'desc': 'test'
        }
        result = self.getImpl().KButil_Merge_FeatureSet_Collection(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseCollections.FeatureSet'
        output_ref = self.getWsName()+'/'+output_name
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':output_ref}]})
        self.assertEqual(len(info_list),1)
        output_info = info_list[0]
        self.assertEqual(output_info[1],output_name)
        self.assertEqual(output_info[2].split('-')[0],output_type)
        output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
        self.assertEqual(len(output_obj['element_ordering']),3)
        pass


    #### test_KButil_Merge_GenomeSets():
    ##
    def test_KButil_Merge_GenomeSets (self):
        method = 'KButil_Merge_GenomeSets'

        print ("\n\nRUNNING: test_KButil_Merge_GenomeSets()")
        print ("=======================================\n\n")

        # input_data
        reference_prok_genomes_WS = 'ReferenceDataManager'  # PROD and CI
        genome_ref_1 = reference_prok_genomes_WS+'/GCF_001566335.1/1'  # E. coli K-12 MG1655
        genome_ref_2 = reference_prok_genomes_WS+'/GCF_000021385.1/1'  # D. vulgaris str. 'Miyazaki F'
        genome_ref_3 = reference_prok_genomes_WS+'/GCF_900129775.1/1'  # Halobaculum gomorrense (16 contigs)
        #genome_id_feature_id_delim = '.f:'
        #feature_id_1 = 'AWN69_RS07145'
        #feature_id_2 = 'DVMF_RS00005'
        #feature_id_3 = 'BUE16_RS15805'

        # GenomeSet 1
        genomeSet_obj_1 = { 'description': 'test genomeSet 1',
                            'elements': { 'genome_1': { 'ref': genome_ref_1 },
                                          'genome_2': { 'ref': genome_ref_2 }
                                      }
                        }            
        provenance = [{}]
        genomeSet_info = self.getWsClient().save_objects({
            'workspace': self.getWsName(), 
            'objects': [
                {
                    'type': 'KBaseSearch.GenomeSet',
                    'data': genomeSet_obj_1,
                    'name': 'test_genomeSet_1',
                    'meta': {},
                    'provenance': provenance
                }
            ]})[0]

        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        genomeSet_ref_1 = str(genomeSet_info[WSID_I])+'/'+str(genomeSet_info[OBJID_I])+'/'+str(genomeSet_info[VERSION_I])

        # GenomeSet 2
        genomeSet_obj_2 = { 'description': 'test genomeSet 2',
                            'elements': { 'genome_3': { 'ref': genome_ref_3 }
                                      }
                        }            
        provenance = [{}]
        genomeSet_info = self.getWsClient().save_objects({
            'workspace': self.getWsName(), 
            'objects': [
                {
                    'type': 'KBaseSearch.GenomeSet',
                    'data': genomeSet_obj_2,
                    'name': 'test_genomeSet_2',
                    'meta': {},
                    'provenance': provenance
                }
            ]})[0]

        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        genomeSet_ref_2 = str(genomeSet_info[WSID_I])+'/'+str(genomeSet_info[OBJID_I])+'/'+str(genomeSet_info[VERSION_I])


        # run method
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': [genomeSet_ref_1, genomeSet_ref_2],
            'output_name': base_output_name,
            'desc': 'test'
        }
        result = self.getImpl().KButil_Merge_GenomeSets(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseSearch.GenomeSet'
        output_ref = self.getWsName()+'/'+output_name
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':output_ref}]})
        self.assertEqual(len(info_list),1)
        output_info = info_list[0]
        self.assertEqual(output_info[1],output_name)
        self.assertEqual(output_info[2].split('-')[0],output_type)
        output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
        self.assertEqual(len(output_obj['elements'].keys()),3)
        pass


    #### test_KButil_Build_GenomeSet():
    ##
    def test_KButil_Build_GenomeSet (self):
        method = 'KButil_Build_GenomeSet'

        print ("\n\nRUNNING: test_KButil_Build_GenomeSet()")
        print ("======================================\n\n")

        # input_data
        reference_prok_genomes_WS = 'ReferenceDataManager'  # PROD and CI
        genome_ref_1 = reference_prok_genomes_WS+'/GCF_001566335.1/1'  # E. coli K-12 MG1655
        genome_ref_2 = reference_prok_genomes_WS+'/GCF_000021385.1/1'  # D. vulgaris str. 'Miyazaki F'
        genome_ref_3 = reference_prok_genomes_WS+'/GCF_900129775.1/1'  # Halobaculum gomorrense (16 contigs)
        #genome_id_feature_id_delim = '.f:'
        #feature_id_1 = 'AWN69_RS07145'
        #feature_id_2 = 'DVMF_RS00005'
        #feature_id_3 = 'BUE16_RS15805'

        # run method
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': [genome_ref_1, genome_ref_2, genome_ref_3],
            'output_name': base_output_name,
            'desc': 'test'
        }
        result = self.getImpl().KButil_Build_GenomeSet(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseSearch.GenomeSet'
        output_ref = self.getWsName()+'/'+output_name
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':output_ref}]})
        self.assertEqual(len(info_list),1)
        output_info = info_list[0]
        self.assertEqual(output_info[1],output_name)
        self.assertEqual(output_info[2].split('-')[0],output_type)
        output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
        self.assertEqual(len(output_obj['elements'].keys()),3)
        pass


    #### test_KButil_Build_GenomeSet_from_FeatureSet():
    ##
    def test_KButil_Build_GenomeSet_from_FeatureSet (self):
        method = 'KButil_Build_GenomeSet_from_FeatureSet'

        print ("\n\nRUNNING: test_KButil_Build_GenomeSet_from_FeatureSet()")
        print ("======================================================\n\n")

        # input_data
        reference_prok_genomes_WS = 'ReferenceDataManager'  # PROD and CI
        genome_ref_1 = reference_prok_genomes_WS+'/GCF_001566335.1/1'  # E. coli K-12 MG1655
        genome_ref_2 = reference_prok_genomes_WS+'/GCF_000021385.1/1'  # D. vulgaris str. 'Miyazaki F'
        genome_ref_3 = reference_prok_genomes_WS+'/GCF_900129775.1/1'  # Halobaculum gomorrense (16 contigs)
        genome_id_feature_id_delim = '.f:'
        feature_id_1 = 'AWN69_RS07145'
        feature_id_2 = 'DVMF_RS00005'
        feature_id_3 = 'BUE16_RS15805'

        # featureSet
        featureSet_obj = { 'description': 'test featureSet',
                           'element_ordering': [
                               feature_id_1,
                               feature_id_2,
                               feature_id_3
                           ],
                           'elements': { 
                               feature_id_1: [genome_ref_1],
                               feature_id_2: [genome_ref_2],
                               feature_id_3: [genome_ref_3]
                           }
                       }
        provenance = [{}]
        featureSet_info = self.getWsClient().save_objects({
            'workspace': self.getWsName(), 
            'objects': [
                {
                    'type': 'KBaseCollections.FeatureSet',
                    'data': featureSet_obj,
                    'name': 'test_featureSet',
                    'meta': {},
                    'provenance': provenance
                }
            ]})[0]

        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        featureSet_ref = str(featureSet_info[WSID_I])+'/'+str(featureSet_info[OBJID_I])+'/'+str(featureSet_info[VERSION_I])

        # run method
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_ref': featureSet_ref,
            'output_name': base_output_name,
            'desc': 'test'
        }
        result = self.getImpl().KButil_Build_GenomeSet_from_FeatureSet(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseSearch.GenomeSet'
        output_ref = self.getWsName()+'/'+output_name
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':output_ref}]})
        self.assertEqual(len(info_list),1)
        output_info = info_list[0]
        self.assertEqual(output_info[1],output_name)
        self.assertEqual(output_info[2].split('-')[0],output_type)
        output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
        self.assertEqual(len(output_obj['elements'].keys()),3)
        pass


    #### test_KButil_Add_Genomes_to_GenomeSet():
    ##
    def test_KButil_Add_Genomes_to_GenomeSet (self):
        method = 'KButil_Add_Genomes_to_GenomeSet'

        print ("\n\nRUNNING: test_KButil_Add_Genomes_to_GenomeSet()")
        print ("===============================================\n\n")

        # input_data
        reference_prok_genomes_WS = 'ReferenceDataManager'  # PROD and CI
        genome_ref_1 = reference_prok_genomes_WS+'/GCF_001566335.1/1'  # E. coli K-12 MG1655
        genome_ref_2 = reference_prok_genomes_WS+'/GCF_000021385.1/1'  # D. vulgaris str. 'Miyazaki F'
        genome_ref_3 = reference_prok_genomes_WS+'/GCF_900129775.1/1'  # Halobaculum gomorrense (16 contigs)
        #genome_id_feature_id_delim = '.f:'
        #feature_id_1 = 'AWN69_RS07145'
        #feature_id_2 = 'DVMF_RS00005'
        #feature_id_3 = 'BUE16_RS15805'

        # GenomeSet 1
        genomeSet_obj_1 = { 'description': 'test genomeSet 1',
                            'elements': { 'genome_1': { 'ref': genome_ref_1 }
                                      }
                        }            
        provenance = [{}]
        genomeSet_info = self.getWsClient().save_objects({
            'workspace': self.getWsName(), 
            'objects': [
                {
                    'type': 'KBaseSearch.GenomeSet',
                    'data': genomeSet_obj_1,
                    'name': 'test_genomeSet_1',
                    'meta': {},
                    'provenance': provenance
                }
            ]})[0]

        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        genomeSet_ref_1 = str(genomeSet_info[WSID_I])+'/'+str(genomeSet_info[OBJID_I])+'/'+str(genomeSet_info[VERSION_I])


        # run method
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_genome_refs': [genome_ref_2, genome_ref_3],
            'input_genomeset_ref': genomeSet_ref_1,
            'output_name': base_output_name,
            'desc': 'test'
        }
        result = self.getImpl().KButil_Add_Genomes_to_GenomeSet(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseSearch.GenomeSet'
        output_ref = self.getWsName()+'/'+output_name
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':output_ref}]})
        self.assertEqual(len(info_list),1)
        output_info = info_list[0]
        self.assertEqual(output_info[1],output_name)
        self.assertEqual(output_info[2].split('-')[0],output_type)
        output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
        self.assertEqual(len(output_obj['elements'].keys()),3)
        pass


    #### test_KButil_Concat_MSAs():
    ##
    def test_KButil_Concat_MSAs (self):
        method = 'KButil_Concat_MSAs'

        print ("\n\nRUNNING: test_KButil_Concat_MSAs()")
        print ("==================================\n\n")

        # MSA
        MSA_json_file = os.path.join('data', 'DsrA.MSA.json')
        with open (MSA_json_file, 'r', 0) as MSA_json_fh:
            MSA_obj = json.load(MSA_json_fh)
        provenance = [{}]
        MSA_info_list = self.getWsClient().save_objects({
            'workspace': self.getWsName(), 
            'objects': [
                {
                    'type': 'KBaseTrees.MSA',
                    'data': MSA_obj,
                    'name': 'test_MSA_1',
                    'meta': {},
                    'provenance': provenance
                },
                {
                    'type': 'KBaseTrees.MSA',
                    'data': MSA_obj,
                    'name': 'test_MSA_2',
                    'meta': {},
                    'provenance': provenance
                },
                {
                    'type': 'KBaseTrees.MSA',
                    'data': MSA_obj,
                    'name': 'test_MSA_3',
                    'meta': {},
                    'provenance': provenance
                }
            ]})
        [OBJID_I, NAME_I, TYPE_I, SAVE_DATE_I, VERSION_I, SAVED_BY_I, WSID_I, WORKSPACE_I, CHSUM_I, SIZE_I, META_I] = range(11)  # object_info tuple
        MSA_ref_1 = str(MSA_info_list[0][WSID_I])+'/'+str(MSA_info_list[0][OBJID_I])+'/'+str(MSA_info_list[0][VERSION_I])
        MSA_ref_2 = str(MSA_info_list[1][WSID_I])+'/'+str(MSA_info_list[1][OBJID_I])+'/'+str(MSA_info_list[1][VERSION_I])
        MSA_ref_3 = str(MSA_info_list[2][WSID_I])+'/'+str(MSA_info_list[2][OBJID_I])+'/'+str(MSA_info_list[2][VERSION_I])

        # run method
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': [MSA_ref_1, MSA_ref_2, MSA_ref_3],
            'output_name': base_output_name,
            'desc': 'test'
        }
        result = self.getImpl().KButil_Concat_MSAs(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseTrees.MSA'
        output_ref = self.getWsName()+'/'+output_name
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':output_ref}]})
        self.assertEqual(len(info_list),1)
        output_info = info_list[0]
        self.assertEqual(output_info[1],output_name)
        self.assertEqual(output_info[2].split('-')[0],output_type)
        output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
        self.assertEqual(len(output_obj['row_order']), len(MSA_obj['row_order']))
        self.assertEqual(output_obj['alignment_length'], 3*MSA_obj['alignment_length'])
        pass


    #### test_KButil_Build_ReadsSet()
    ##
    def test_KButil_Build_ReadsSet (self):
        method = 'KButil_Build_ReadsSet'
        
        print ("\n\nRUNNING: test_KButil_Build_ReadsSet()")
        print ("=====================================\n\n")

        # figure out where the test data lives
        pe_lib_info_1 = self.getPairedEndLibInfo('test_quick', lib_i=0)
        pprint(pe_lib_info_1)
        pe_lib_info_2 = self.getPairedEndLibInfo('small', lib_i=1)
        pprint(pe_lib_info_2)
        pe_lib_info_3 = self.getPairedEndLibInfo('small_2',lib_i=2)
        pprint(pe_lib_info_3)

        # run method
        input_refs = [ str(pe_lib_info_1[6])+'/'+str(pe_lib_info_1[0]),
                       str(pe_lib_info_2[6])+'/'+str(pe_lib_info_2[0]),
                       str(pe_lib_info_3[6])+'/'+str(pe_lib_info_3[0])
                   ]
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': input_refs,
            'output_name': base_output_name,
            'desc':'test build readsSet'
        }
        result = self.getImpl().KButil_Build_ReadsSet(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseSets.ReadsSet'
        output_ref = self.getWsName() + '/' + output_name
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':output_ref}]})
        self.assertEqual(len(info_list),1)
        readsLib_info = info_list[0]
        self.assertEqual(readsLib_info[1],output_name)
        self.assertEqual(readsLib_info[2].split('-')[0],output_type)
        output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
        self.assertEqual(len(output_obj['items']), 3)
        pass


    #### test_KButil_Split_Reads():
    ##
    def test_KButil_Split_Reads (self):
        method = 'KButil_Split_Reads'
        
        print ("\n\nRUNNING: test_KButil_Split_Reads()")
        print ("==================================\n\n")

        # figure out where the test data lives
        pe_lib_info = self.getPairedEndLibInfo('small_2')
        pprint(pe_lib_info)

        # Object Info Contents
        # 0 - obj_id objid
        # 1 - obj_name name
        # 2 - type_string type
        # 3 - timestamp save_date
        # 4 - int version
        # 5 - username saved_by
        # 6 - ws_id wsid
        # 7 - ws_name workspace
        # 8 - string chsum
        # 9 - int size
        # 10 - usermeta meta


        # run method
        split_num = 4
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_ref': str(pe_lib_info[6])+'/'+str(pe_lib_info[0]),
            'split_num': split_num,
            'output_name': base_output_name,
            'desc':'test split'
        }
        result = self.getImpl().KButil_Split_Reads(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name+'_paired-0'
        output_type = 'KBaseFile.PairedEndLibrary'
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':pe_lib_info[7] + '/' + output_name}]})
        self.assertEqual(len(info_list),1)
        readsLib_info = info_list[0]
        self.assertEqual(readsLib_info[1],output_name)
        self.assertEqual(readsLib_info[2].split('-')[0],output_type)

        output_name = base_output_name+'_paired-'+str(split_num-1)
        output_type = 'KBaseFile.PairedEndLibrary'
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':pe_lib_info[7] + '/' + output_name}]})
        self.assertEqual(len(info_list),1)
        readsLib_info = info_list[0]
        self.assertEqual(readsLib_info[1],output_name)
        self.assertEqual(readsLib_info[2].split('-')[0],output_type)
        pass


    #### test_KButil_Random_Subsample_Reads():
    ##
    def test_KButil_Random_Subsample_Reads (self):
        method = 'KButil_Random_Subsample_Reads'
        
        print ("\n\nRUNNING: test_KButil_Random_Subsample_Reads()")
        print ("=============================================\n\n")

        # figure out where the test data lives
        pe_lib_info = self.getPairedEndLibInfo('small_2')
        pprint(pe_lib_info)

        # run method
        split_num = 4
        reads_num = 2500
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_ref': str(pe_lib_info[6])+'/'+str(pe_lib_info[0]),
            'subsample_fraction': {'split_num': split_num,
                                   'reads_num': reads_num
                               },
            'output_name': base_output_name,
            'desc':'test random subsample',
            'seed': 1
        }
        result = self.getImpl().KButil_Random_Subsample_Reads(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name+'_paired-0'
        output_type = 'KBaseFile.PairedEndLibrary'
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':pe_lib_info[7] + '/' + output_name}]})
        self.assertEqual(len(info_list),1)
        readsLib_info = info_list[0]
        self.assertEqual(readsLib_info[1],output_name)
        self.assertEqual(readsLib_info[2].split('-')[0],output_type)

        output_name = base_output_name+'_paired-'+str(split_num-1)
        output_type = 'KBaseFile.PairedEndLibrary'
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':pe_lib_info[7] + '/' + output_name}]})
        self.assertEqual(len(info_list),1)
        readsLib_info = info_list[0]
        self.assertEqual(readsLib_info[1],output_name)
        self.assertEqual(readsLib_info[2].split('-')[0],output_type)
        pass


    #### test_KButil_Merge_ReadsSet_to_OneLibrary()
    ##
    def test_KButil_Merge_ReadsSet_to_OneLibrary (self):
        method = 'KButil_Merge_ReadsSet_to_OneLibrary'

        print ("\n\nRUNNING: test_KButil_Merge_ReadsSet_to_OneLibrary()")
        print ("===================================================\n\n")

        # figure out where the test data lives
        pe_lib_set_info = self.getPairedEndLib_SetInfo(['test_quick','small_2'])
        pprint(pe_lib_set_info)

        # run method
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_ref': str(pe_lib_set_info[6])+'/'+str(pe_lib_set_info[0]),
            'output_name': base_output_name,
            'desc':'test merge'
        }
        result = self.getImpl().KButil_Merge_ReadsSet_to_OneLibrary(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseFile.PairedEndLibrary'
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':self.getWsName() + '/' + output_name}]})
        self.assertEqual(len(info_list),1)
        readsLib_info = info_list[0]
        self.assertEqual(readsLib_info[1],output_name)
        self.assertEqual(readsLib_info[2].split('-')[0],output_type)
        pass


    #### test_KButil_Merge_MultipleReadsLibs_to_OneLibrary()
    ##
    def test_KButil_Merge_MultipleReadsLibs_to_OneLibrary (self):
        method = 'KButil_Merge_MultipleReadsLibs_to_OneLibrary'

        print ("\n\nRUNNING: test_KButil_Merge_MultipleReadsLibs_to_OneLibrary()")
        print ("============================================================\n\n")

        # figure out where the test data lives
        pe_lib_info_1 = self.getPairedEndLibInfo('test_quick', lib_i=0)
        pprint(pe_lib_info_1)
        pe_lib_info_2 = self.getPairedEndLibInfo('small', lib_i=1)
        pprint(pe_lib_info_2)
        pe_lib_info_3 = self.getPairedEndLibInfo('small_2',lib_i=2)
        pprint(pe_lib_info_3)

        # run method
        input_refs = [ str(pe_lib_info_1[6])+'/'+str(pe_lib_info_1[0]),
                       str(pe_lib_info_2[6])+'/'+str(pe_lib_info_2[0]),
                       str(pe_lib_info_3[6])+'/'+str(pe_lib_info_3[0])
                   ]
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': input_refs,
            'output_name': base_output_name,
            'desc':'test merge'
        }
        result = self.getImpl().KButil_Merge_MultipleReadsLibs_to_OneLibrary(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseFile.PairedEndLibrary'
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':self.getWsName() + '/' + output_name}]})
        self.assertEqual(len(info_list),1)
        readsLib_info = info_list[0]
        self.assertEqual(readsLib_info[1],output_name)
        self.assertEqual(readsLib_info[2].split('-')[0],output_type)
        pass


    #### test_KButil_Merge_MultipleReadsSets_to_OneReadsSet()
    ##
    def test_KButil_Merge_MultipleReadsSets_to_OneReadsSet (self):
        method = 'KButil_Merge_MultipleReadsSets_to_OneReadsSet'

        print ("\n\nRUNNING: test_KButil_Merge_MultipleReadsSetss_to_OneReadsSet()")
        print ("==============================================================\n\n")

        # figure out where the test data lives
        lib_basenames = ['test_quick', 'small', 'small_2']
        pe_lib_info = []
        lib_refs = []
        for lib_i,lib_basename in enumerate(lib_basenames):
            this_info = self.getPairedEndLibInfo(lib_basename, lib_i=lib_i)
            pe_lib_info.append(this_info)
            pprint(this_info)

            lib_refs.append(str(this_info[6])+'/'+str(this_info[0])+'/'+str(this_info[4]))

        # make readsSet 1
        items = [ {'ref': lib_refs[0],
                   'label': lib_basenames[0]
               },
                  {'ref': lib_refs[1],
                   'label': lib_basenames[1]
               }]
        desc = 'test ReadsSet 1'
        readsSet_obj_1 = { 'description': desc,
                           'items': items
                       }
        name = 'TEST_READSET_1'
        new_obj_set_info = self.wsClient.save_objects({
            'workspace':self.getWsName(),
            'objects':[
                {
                    'type':'KBaseSets.ReadsSet',
                    'data':readsSet_obj_1,
                    'name':name,
                    'meta':{},
                    'provenance':[
                        {
                            'service':'kb_util_dylan',
                            'method':'test_kb_util_dylan'
                        }
                    ]
                }]
        })[0]
        readsSet_ref_1 = str(new_obj_set_info[6]) +'/'+ str(new_obj_set_info[0]) +'/'+ str(new_obj_set_info[4])

        # make readsSet 2
        items = [ {'ref': lib_refs[2],
                   'label': lib_basenames[2]
               }]
        desc = 'test ReadsSet 2'
        readsSet_obj_2 = { 'description': desc,
                           'items': items
                       }
        name = 'TEST_READSET_2'
        new_obj_set_info = self.wsClient.save_objects({
            'workspace':self.getWsName(),
            'objects':[
                {
                    'type':'KBaseSets.ReadsSet',
                    'data':readsSet_obj_2,
                    'name':name,
                    'meta':{},
                    'provenance':[
                        {
                            'service':'kb_util_dylan',
                            'method':'test_kb_util_dylan'
                        }
                    ]
                }]
        })[0]
        readsSet_ref_2 = str(new_obj_set_info[6]) +'/'+ str(new_obj_set_info[0]) +'/'+ str(new_obj_set_info[4])

        # run method
        input_refs = [ readsSet_ref_1, readsSet_ref_2 ]
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': input_refs,
            'output_name': base_output_name,
            'desc':'test merge'
        }
        result = self.getImpl().KButil_Merge_MultipleReadsSets_to_OneReadsSet(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseSets.ReadsSet'
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':self.getWsName() + '/' + output_name}]})
        self.assertEqual(len(info_list),1)
        output_info = info_list[0]
        self.assertEqual(output_info[1],output_name)
        self.assertEqual(output_info[2].split('-')[0],output_type)
        output_ref = self.getWsName()+'/'+output_name
        output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
        self.assertEqual(len(output_obj['items']),3)
        pass


    #### test_KButil_Extract_Unpaired_Reads_and_Synchronize_Pairs():
    ##
    def test_KButil_Extract_Unpaired_Reads_and_Synchronize_Pairs (self):
        method = 'KButil_Extract_Unpaired_Reads_and_Synchronize_Pairs'

        print ("\n\nRUNNING: test_KButil_Extract_Unpaired_Reads_and_Synchronize_Pairs()")
        print ("===================================================================\n\n")

        # figure out where the test data lives
        lib_basenames = ['test_quick','small_2','small']
        pe_lib_set_info = self.getPairedEndLib_SetInfo(lib_basenames)
        pprint(pe_lib_set_info)

        # run method
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_ref': str(pe_lib_set_info[6])+'/'+str(pe_lib_set_info[0]),
            'output_name': base_output_name,
            'desc':'test hygiene'
        }
        result = self.getImpl().KButil_Extract_Unpaired_Reads_and_Synchronize_Pairs(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        reads_name_ext = "_paired_synched"
        output_name = base_output_name + reads_name_ext
        output_type = 'KBaseSets.ReadsSet'
        output_ref = self.getWsName() + '/' + output_name
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':output_ref}]})
        self.assertEqual(len(info_list),1)
        output_info = info_list[0]
        self.assertEqual(output_info[1],output_name)
        self.assertEqual(output_info[2].split('-')[0],output_type)
        output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
        print ('OUTPUT_OBJ:')
        pprint(output_obj)
        self.assertEqual(len(output_obj['items']),len(lib_basenames))
        pass


    #### test_KButil_Translate_ReadsLibs_QualScores()
    ##
    def test_KButil_Translate_ReadsLibs_QualScores (self):
        method = 'KButil_Translate_ReadsLibs_QualScores'

        print ("\n\nRUNNING: test_KButil_Translate_ReadsLibs_QualScores()")
        print ("=====================================================\n\n")

        # figure out where the test data lives
        lib_basenames = ['test_quick', 'small']
        lib_obj_names = []
        input_refs = []
        for lib_i,lib_basename in enumerate(lib_basenames):
            pe_lib_info = self.getPairedEndLibInfo(lib_basename+'-q64_5recs', lib_i=lib_i)
            pprint(pe_lib_info)
            lib_obj_names.append(str(pe_lib_info[1]))
            input_refs.append(str(pe_lib_info[6])+'/'+str(pe_lib_info[0])+'/'+str(pe_lib_info[4]))

        # run method
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': input_refs
        }
        result = self.getImpl().KButil_Translate_ReadsLibs_QualScores(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        for lib_i,lib_basename in enumerate(lib_basenames):
            output_name = lib_obj_names[lib_i]+'.phred33'
            output_type = 'KBaseFile.PairedEndLibrary'
            output_ref = self.getWsName()+'/'+output_name
            info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':output_ref}]})
            self.assertEqual(len(info_list),1)
            output_info = info_list[0]
            self.assertEqual(output_info[1],output_name)
            self.assertEqual(output_info[2].split('-')[0],output_type)
        pass


    #### test_KButil_AddInsertLen_to_ReadsLibs()
    ##
    def test_KButil_AddInsertLen_to_ReadsLibs (self):
        method = 'KButil_AddInsertLen_to_ReadsLibs'

        print ("\n\nRUNNING: test_KButil_AddInsertLen_to_ReadsLibs()")
        print ("================================================\n\n")

        # figure out where the test data lives
        lib_basenames = ['test_quick', 'small']
        lib_obj_names = []
        input_refs = []
        for lib_i,lib_basename in enumerate(lib_basenames):
            pe_lib_info = self.getPairedEndLibInfo(lib_basename, lib_i=lib_i)
            pprint(pe_lib_info)
            lib_obj_names.append(str(pe_lib_info[1]))
            input_refs.append(str(pe_lib_info[6])+'/'+str(pe_lib_info[0])+'/'+str(pe_lib_info[4]))

        # run method
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': input_refs,
            'insert_len': '450.0',
            'insert_stddev': '15.0'
        }
        result = self.getImpl().KButil_AddInsertLen_to_ReadsLibs(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        for lib_i,lib_basename in enumerate(lib_basenames):
            output_name = lib_obj_names[lib_i]
            output_type = 'KBaseFile.PairedEndLibrary'
            output_ref = self.getWsName()+'/'+output_name
            info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':output_ref}]})
            self.assertEqual(len(info_list),1)
            output_info = info_list[0]
            self.assertEqual(output_info[1],output_name)
            self.assertEqual(output_info[2].split('-')[0],output_type)
            output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
            print ('OUTPUT_OBJ:')
            pprint(output_obj)
            self.assertEqual(output_obj['insert_size_mean'],450.0)
            self.assertEqual(output_obj['insert_size_std_dev'],15.0)
        pass


    #### test_KButil_Build_AssemblySet()
    ##
    def test_KButil_Build_AssemblySet (self):
        method = 'KButil_Build_AssemblySet'
        
        print ("\n\nRUNNING: test_KButil_Build_AssemblySet()")
        print ("========================================\n\n")

        # upload test data
        try:
            auClient = AssemblyUtil(self.callbackURL, token=self.token)
        except Exception as e:
            raise ValueError('Unable to instantiate auClient with callbackURL: '+ self.callbackURL +' ERROR: ' + str(e))
        ass_file_1 = 'assembly_1.fa'
        ass_file_2 = 'assembly_2.fa'
        ass_path_1 = os.path.join(self.scratch, ass_file_1)
        ass_path_2 = os.path.join(self.scratch, ass_file_2)
        shutil.copy(os.path.join("data", ass_file_1), ass_path_1)
        shutil.copy(os.path.join("data", ass_file_2), ass_path_2)
        ass_ref_1 = auClient.save_assembly_from_fasta({
            'file': {'path': ass_path_1},
            'workspace_name': self.getWsName(),
            'assembly_name': 'assembly_1'
        })
        ass_ref_2 = auClient.save_assembly_from_fasta({
            'file': {'path': ass_path_2},
            'workspace_name': self.getWsName(),
            'assembly_name': 'assembly_1'
        })

        # run method
        input_refs = [ ass_ref_1, ass_ref_2 ]
        base_output_name = method+'_output'
        params = {
            'workspace_name': self.getWsName(),
            'input_refs': input_refs,
            'output_name': base_output_name,
            'desc':'test build assemblySet'
        }
        result = self.getImpl().KButil_Build_AssemblySet(self.getContext(),params)
        print('RESULT:')
        pprint(result)

        # check the output
        output_name = base_output_name
        output_type = 'KBaseSets.AssemblySet'
        output_ref = self.getWsName() + '/' + output_name
        info_list = self.getWsClient().get_object_info_new({'objects':[{'ref':output_ref}]})
        self.assertEqual(len(info_list),1)
        assemblySet_info = info_list[0]
        self.assertEqual(assemblySet_info[1],output_name)
        self.assertEqual(assemblySet_info[2].split('-')[0],output_type)
        output_obj = self.getWsClient().get_objects2({'objects': [{'ref': output_ref}]})['data'][0]['data']
        self.assertEqual(len(output_obj['items']), len(input_refs))
        pass
