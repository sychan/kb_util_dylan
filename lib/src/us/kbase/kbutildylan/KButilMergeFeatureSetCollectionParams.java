
package us.kbase.kbutildylan;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: KButil_Merge_FeatureSet_Collection_Params</p>
 * <pre>
 * KButil_Merge_FeatureSet_Collection()
 * **
 * **  Method for merging FeatureSets
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "workspace_name",
    "input_refs",
    "output_name",
    "desc"
})
public class KButilMergeFeatureSetCollectionParams {

    @JsonProperty("workspace_name")
    private String workspaceName;
    @JsonProperty("input_refs")
    private String inputRefs;
    @JsonProperty("output_name")
    private String outputName;
    @JsonProperty("desc")
    private String desc;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("workspace_name")
    public String getWorkspaceName() {
        return workspaceName;
    }

    @JsonProperty("workspace_name")
    public void setWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
    }

    public KButilMergeFeatureSetCollectionParams withWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
        return this;
    }

    @JsonProperty("input_refs")
    public String getInputRefs() {
        return inputRefs;
    }

    @JsonProperty("input_refs")
    public void setInputRefs(String inputRefs) {
        this.inputRefs = inputRefs;
    }

    public KButilMergeFeatureSetCollectionParams withInputRefs(String inputRefs) {
        this.inputRefs = inputRefs;
        return this;
    }

    @JsonProperty("output_name")
    public String getOutputName() {
        return outputName;
    }

    @JsonProperty("output_name")
    public void setOutputName(String outputName) {
        this.outputName = outputName;
    }

    public KButilMergeFeatureSetCollectionParams withOutputName(String outputName) {
        this.outputName = outputName;
        return this;
    }

    @JsonProperty("desc")
    public String getDesc() {
        return desc;
    }

    @JsonProperty("desc")
    public void setDesc(String desc) {
        this.desc = desc;
    }

    public KButilMergeFeatureSetCollectionParams withDesc(String desc) {
        this.desc = desc;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((((("KButilMergeFeatureSetCollectionParams"+" [workspaceName=")+ workspaceName)+", inputRefs=")+ inputRefs)+", outputName=")+ outputName)+", desc=")+ desc)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
