import xml.etree.ElementTree as ET
from xml.dom import minidom


def generate_jmeter_testplan(endpoint, method, param_mapping, csv_filename="data.csv", thread_count=1):
    def create_element_with_text(tag, attrib, text):
        elem = ET.Element(tag, attrib)
        elem.text = text
        return elem

    def create_http_sampler(method, path, domain, port, protocol, params):
        sampler = ET.Element("HTTPSamplerProxy", {
            "guiclass": "HttpTestSampleGui",
            "testclass": "HTTPSamplerProxy",
            "testname": f"{method} {path}",
            "enabled": "true"
        })
        sampler.append(create_element_with_text("stringProp", {"name": "HTTPSampler.domain"}, domain))
        sampler.append(create_element_with_text("stringProp", {"name": "HTTPSampler.port"}, port))
        sampler.append(create_element_with_text("stringProp", {"name": "HTTPSampler.protocol"}, protocol))
        sampler.append(create_element_with_text("stringProp", {"name": "HTTPSampler.path"}, path))
        sampler.append(create_element_with_text("stringProp", {"name": "HTTPSampler.method"}, method))

        # Always required fields
        sampler.append(create_element_with_text("boolProp", {"name": "HTTPSampler.follow_redirects"}, "true"))
        sampler.append(create_element_with_text("boolProp", {"name": "HTTPSampler.auto_redirects"}, "false"))
        sampler.append(create_element_with_text("boolProp", {"name": "HTTPSampler.use_keepalive"}, "true"))
        sampler.append(create_element_with_text("boolProp", {"name": "HTTPSampler.DO_MULTIPART_POST"}, "false"))
        sampler.append(create_element_with_text("stringProp", {"name": "HTTPSampler.embedded_url_re"}, ""))

        # If POST, add body params
        if method.upper() != "GET":
            args = ET.Element("elementProp", {
                "name": "HTTPsampler.Arguments",
                "elementType": "Arguments",
                "guiclass": "HTTPArgumentsPanel",
                "testclass": "Arguments",
                "enabled": "true"
            })
            coll = ET.SubElement(args, "collectionProp", {"name": "Arguments.arguments"})
            for k, v in params.items():
                ep = ET.SubElement(coll, "elementProp", {"name": k, "elementType": "HTTPArgument"})
                ET.SubElement(ep, "boolProp", {"name": "HTTPArgument.always_encode"}).text = "false"
                ET.SubElement(ep, "stringProp", {"name": "Argument.name"}).text = k
                ET.SubElement(ep, "stringProp", {"name": "Argument.value"}).text = v
                ET.SubElement(ep, "stringProp", {"name": "Argument.metadata"}).text = "="
            sampler.append(args)

        return sampler

    # 🧱 Build JMeter XML structure
    root = ET.Element("jmeterTestPlan", {"version": "1.2", "properties": "5.0", "jmeter": "5.2.1"})
    hash_tree = ET.SubElement(root, "hashTree")

    # Test Plan
    test_plan = ET.SubElement(hash_tree, "TestPlan", {
        "guiclass": "TestPlanGui",
        "testclass": "TestPlan",
        "testname": "Test Plan",
        "enabled": "true"
    })
    ET.SubElement(test_plan, "stringProp", {"name": "TestPlan.comments"})
    ET.SubElement(test_plan, "boolProp", {"name": "TestPlan.functional_mode"}).text = "false"
    ET.SubElement(test_plan, "boolProp", {"name": "TestPlan.tearDown_on_shutdown"}).text = "true"
    ET.SubElement(test_plan, "boolProp", {"name": "TestPlan.serialize_threadgroups"}).text = "false"
    ET.SubElement(test_plan, "elementProp", {
        "name": "TestPlan.user_defined_variables",
        "elementType": "Arguments",
        "guiclass": "ArgumentsPanel",
        "testclass": "Arguments",
        "enabled": "true"
    }).append(ET.Element("collectionProp", {"name": "Arguments.arguments"}))
    ET.SubElement(test_plan, "stringProp", {"name": "TestPlan.user_define_classpath"})

    test_plan_ht = ET.SubElement(hash_tree, "hashTree")

    # Thread Group
    thread_group = ET.SubElement(test_plan_ht, "ThreadGroup", {
        "guiclass": "ThreadGroupGui",
        "testclass": "ThreadGroup",
        "testname": "Thread Group",
        "enabled": "true"
    })
    ET.SubElement(thread_group, "stringProp", {"name": "ThreadGroup.num_threads"}).text = str(thread_count)
    ET.SubElement(thread_group, "stringProp", {"name": "ThreadGroup.ramp_time"}).text = "1"
    ET.SubElement(thread_group, "boolProp", {"name": "ThreadGroup.scheduler"}).text = "false"
    ET.SubElement(thread_group, "stringProp", {"name": "ThreadGroup.duration"}).text = ""
    ET.SubElement(thread_group, "stringProp", {"name": "ThreadGroup.delay"}).text = ""

    tg_ht = ET.SubElement(test_plan_ht, "hashTree")

    # CSV Reader
    csv = ET.SubElement(tg_ht, "CSVDataSet", {
        "guiclass": "TestBeanGUI",
        "testclass": "CSVDataSet",
        "testname": "CSV Data Set Config",
        "enabled": "true"
    })
    ET.SubElement(csv, "stringProp", {"name": "filename"}).text = csv_filename
    ET.SubElement(csv, "stringProp", {"name": "fileEncoding"}).text = "UTF-8"
    ET.SubElement(csv, "stringProp", {"name": "variableNames"}).text = ",".join(v.replace("${", "").replace("}", "") for v in param_mapping.values())
    ET.SubElement(csv, "boolProp", {"name": "ignoreFirstLine"}).text = "false"
    ET.SubElement(csv, "stringProp", {"name": "delimiter"}).text = ","
    ET.SubElement(csv, "boolProp", {"name": "quotedData"}).text = "false"
    ET.SubElement(csv, "boolProp", {"name": "recycle"}).text = "true"
    ET.SubElement(csv, "boolProp", {"name": "stopThread"}).text = "false"
    ET.SubElement(csv, "stringProp", {"name": "shareMode"}).text = "shareMode.all"

    ET.SubElement(tg_ht, "hashTree")  # For CSV

    # HTTP Sampler
    method_upper = method.upper()
    path = endpoint.split(" ")[1]
    domain = "fakerestapi.azurewebsites.net"
    protocol = "https"
    port = ""

    sampler = create_http_sampler(method_upper, path, domain, port, protocol, param_mapping)
    tg_ht.append(sampler)
    ET.SubElement(tg_ht, "hashTree")  # For HTTP Sampler

    # Prettify
    xml_str = ET.tostring(root, encoding="utf-8")
    pretty = minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open("auto_test_plan.jmx", "w", encoding="utf-8") as f:
        f.write(pretty)

    print("✅ Fixed & generated: auto_test_plan.jmx (compatible with JMeter 5.2.1)")
