import csv
import argparse
import json
import logging
import os
import sys
from tqdm import tqdm
from model import GPT, StarChat, CodeLLAMA
from util.remove_comments import remove_comments_and_docstrings


fewshot_example_language_4 = {
    'java': [
        {'code':"@Override\n    public ImageSource apply(ImageSource input) {\n        final int[][] pixelMatrix = new int[3][3];\n\n        int w = input.getWidth();\n        int h = input.getHeight();\n\n        int[][] output = new int[h][w];\n\n        for (int j = 1; j < h - 1; j++) {\n            for (int i = 1; i < w - 1; i++) {\n                pixelMatrix[0][0] = input.getR(i - 1, j - 1);\n                pixelMatrix[0][1] = input.getRGB(i - 1, j);\n                pixelMatrix[0][2] = input.getRGB(i - 1, j + 1);\n                pixelMatrix[1][0] = input.getRGB(i, j - 1);\n                pixelMatrix[1][2] = input.getRGB(i, j + 1);\n                pixelMatrix[2][0] = input.getRGB(i + 1, j - 1);\n                pixelMatrix[2][1] = input.getRGB(i + 1, j);\n                pixelMatrix[2][2] = input.getRGB(i + 1, j + 1);\n\n                int edge = (int) convolution(pixelMatrix);\n                int rgb = (edge << 16 | edge << 8 | edge);\n                output[j][i] = rgb;\n            }\n        }\n\n        MatrixSource source = new MatrixSource(output);\n        return source;\n    }", 'nl': "Expects a height mat as input"}
        ,{'code':"public static ComplexNumber Add(ComplexNumber z1, ComplexNumber z2) {\r\n        return new ComplexNumber(z1.real + z2.real, z1.imaginary + z2.imaginary);\r\n    }", 'nl': "Adds two complex numbers."}
        ,{'code':"public void setOutRGB(IntRange outRGB) {\r\n        this.outRed = outRGB;\r\n        this.outGreen = outRGB;\r\n        this.outBlue = outRGB;\r\n\r\n        CalculateMap(inRed, outRGB, mapRed);\r\n        CalculateMap(inGreen, outRGB, mapGreen);\r\n        CalculateMap(inBlue, outRGB, mapBlue);\r\n    }", 'nl': "Set RGB output range."}
        ,{'code':"public Table newRow()\n    {\n        unnest();\n        nest(row = new Block(\"tr\"));\n        if (_defaultRow!=null)\n        {\n            row.setAttributesFrom(_defaultRow);\n            if (_defaultRow.size()>0)\n                row.add(_defaultRow.contents());\n        }\n        cell=null;\n        return this;\n    }", 'nl': 'Create new table row . Attributes set after this call and before a call to newCell or newHeader are considered row attributes.'}
    ],
    'python': [
        {'code': 'def get_meshes_fld(step, var):\n    fld = step.fields[var]\n    if step.geom.twod_xz:\n        xmesh, ymesh = step.geom.x_mesh[:, 0, :], step.geom.z_mesh[:, 0, :]\n        fld = fld[:, 0, :, 0]\n    elif step.geom.cartesian and step.geom.twod_yz:\n        xmesh, ymesh = step.geom.y_mesh[0, :, :], step.geom.z_mesh[0, :, :]\n        fld = fld[0, :, :, 0]\n    else:  \n        xmesh, ymesh = step.geom.x_mesh[0, :, :], step.geom.y_mesh[0, :, :]\n        fld = fld[0, :, :, 0]\n    return xmesh, ymesh, fld', 'nl': 'Return scalar field along with coordinates meshes .'}
        ,{'code': 'def _obtain_token(self):\n        if self.expiration and self.expiration > datetime.datetime.now():\n            return\n        resp = requests.post("{}/1.1/oauth/token".format(API_URL), data={\n            "client_id": self.client_id,\n            "client_secret": self.client_secret,\n            "grant_type": "client_credentials"\n        }).json()\n        if "error" in resp:\n            raise APIError("LibCal Auth Failed: {}, {}".format(resp["error"], resp.get("error_description")))\n        self.expiration = datetime.datetime.now() + datetime.timedelta(seconds=resp["expires_in"])\n        self.token = resp["access_token"]\n        print(self.token)', 'nl': 'Obtain an auth token from client id and client secret .'}
        ,{'code': "def get_byte(self, i):\n        value = []\n        for x in range(2):\n            c = next(i)\n            if c.lower() in _HEX:\n                value.append(c)\n            else:  \n                raise SyntaxError('Invalid byte character at %d!' % (i.index - 1))\n        return ''.join(value)", 'nl': 'Get byte .'}
        ,{'code': "def get_item_children(item):\r\n    children = [item.child(index) for index in range(item.childCount())]\r\n    for child in children[:]:\r\n        others = get_item_children(child)\r\n        if others is not None:\r\n            children += others\r\n    return sorted(children, key=lambda child: child.line)", 'nl': "Return a sorted list of all the children items of item ."}
    ],
    'c': [
        { "code": "void big_key_describe(const struct key *key, struct seq_file *m)\n{\n\tsize_t datalen = (size_t)key->payload.data[big_key_len];\n\n\tseq_puts(m, key->description);\n\n\tif (key_is_positive(key))\n\t\tseq_printf(m, \": %zu [%s]\",\n\t\t\t   datalen,\n\t\t\t   datalen > BIG_KEY_FILE_THRESHOLD ? \"file\" : \"buff\");\n}", "nl": "describe the big_key key"}
        ,{"code": "int event_trace_add_tracer(struct dentry *parent, struct trace_array *tr)\n{\n\tint ret;\n\n\tlockdep_assert_held(&event_mutex);\n\n\tret = create_event_toplevel_files(parent, tr);\n\tif (ret)\n\t\tgoto out;\n\n\tdown_write(&trace_event_sem);\n\t__trace_add_event_dirs(tr);\n\tup_write(&trace_event_sem);\n\n out:\n\treturn ret;\n}", "nl": "add a instance of a trace_array to events"}
        ,{"code": "static bool __init blogic_create_initccbs(struct blogic_adapter *adapter)\n{\n\tint blk_size = BLOGIC_CCB_GRP_ALLOCSIZE * sizeof(struct blogic_ccb);\n\tvoid *blk_pointer;\n\tdma_addr_t blkp;\n\n\twhile (adapter->alloc_ccbs < adapter->initccbs) {\n\t\tblk_pointer = dma_alloc_coherent(&adapter->pci_device->dev,\n\t\t\t\tblk_size, &blkp, GFP_KERNEL);\n\t\tif (blk_pointer == NULL) {\n\t\t\tblogic_err(\"UNABLE TO ALLOCATE CCB GROUP - DETACHING\\n\",\n\t\t\t\t\tadapter);\n\t\t\treturn false;\n\t\t}\n\t\tblogic_init_ccbs(adapter, blk_pointer, blk_size, blkp);\n\t}\n\treturn true;\n}", "nl": "allocates the initial CCBs for Host Adapter"}
        ,{"code": "SWFMovie_addMetadata(SWFMovie movie, const char *xml)\n{\n\tif(!movie->fattrs)\n\t\tmovie->fattrs = newSWFFileAttributes();\n\n\tSWFFileAttributes_hasMetadata(movie->fattrs, 1);\n\t\n\tif(movie->metadata)\n\t\tdestroySWFMetadata(movie->metadata);\n\tmovie->metadata = newSWFMetadata(xml);\n}", 'nl': "adds Metadata to the movie This function inserts a metadata tag into the movie"}
   ],
    'javascript': [
        {'code': 'function promiseWrapper (resolve, reject) {\n            process.on ("exit", (code) => {\n                if (code !== 0) reject (process.stderr.textContent);\n                resolve (process.stdout.textContent);\n            });\n            process.stdin.write (script);\n            process.stdin.end ();\n        }', 'nl': 'Wrapper for the Promise'},
        {'code': 'function() {\n        for( var i = 0; i < this.jobQueue.length; i++ ) {\n            var job = this.jobQueue[i];\n            if ( typeof job.abort === "function" ) {\n                job.abort();\n            }\n        }\n        this.jobQueue = [];\n    }', 'nl': 'Clear any unstarted image loading jobs from the queue .'},
        {'code': 'function computeLineLength(line, tabWidth) {\n            let extraCharacterCount = 0;\n            line.replace(/\\t/gu, (match, offset) => {\n                const totalOffset = offset + extraCharacterCount,\n                    previousTabStopOffset = tabWidth ? totalOffset % tabWidth : 0,\n                    spaceCount = tabWidth - previousTabStopOffset;\n                extraCharacterCount += spaceCount - 1;  \n            });\n            return Array.from(line).length + extraCharacterCount;\n        }', 'nl': 'Computes the length of a line that may contain tabs . The width of each tab will be the number of spaces to the next tab stop .'},
        {'code': "function signals() {\n  function interrupt(signal) {\n    this.log.notice('received %s, scheduling shutdown', signal);\n    this.shutdown(0, process.exit);\n  }\n  interrupt = interrupt.bind(this);\n  function iterate(signal) {\n    if(process.listeners(signal).length) return;\n    process.once(signal, function() {\n      interrupt(signal);\n    })\n  }\n  ['SIGINT', 'SIGTERM'].forEach(iterate.bind(this));\n}", 'nl': 'Register listeners for signals that trigger a shutdown .'}
    ],
    'go': [
        {'code': 'func MaskFrameInPlaceWith(f Frame, m [4]byte) Frame {\n\tf.Header.Masked = true\n\tf.Header.Mask = m\n\tCipher(f.Payload, m, 0)\n\treturn f\n}', 'nl': 'MaskFrameInPlaceWith masks frame with given mask and returns frame with masked payload and Mask header s field set . Note that it applies xor cipher to f . Payload without copying that is it modifies f . Payload inplace .'}
        ,{'code': 'func LoadProvisionerConfigs(configPath string, provisionerConfig *ProvisionerConfiguration) error {\n\tfiles, err := ioutil.ReadDir(configPath)\n\tif err != nil {\n\t\treturn err\n\t}\n\tdata := make(map[string]string)\n\tfor _, file := range files {\n\t\tif !file.IsDir() {\n\t\t\tif strings.Compare(file.Name(), "..data") != 0 {\n\t\t\t\tfileContents, err := ioutil.ReadFile(path.Join(configPath, file.Name()))\n\t\t\t\tif err != nil {\n\t\t\t\t\tglog.Infof("Could not read file: %s due to: %v", path.Join(configPath, file.Name()), err)\n\t\t\t\t\treturn err\n\t\t\t\t}\n\t\t\t\tdata[file.Name()] = string(fileContents)\n\t\t\t}\n\t\t}\n\t}\n\treturn ConfigMapDataToVolumeConfig(data, provisionerConfig)\n}', 'nl': 'LoadProvisionerConfigs loads all configuration into a string and unmarshal it into ProvisionerConfiguration struct . The configuration is stored in the configmap which is mounted as a volume .'}
        ,{'code': 'func PreferredSeries(cfg HasDefaultSeries) string {\n\tif series, ok := cfg.DefaultSeries(); ok {\n\t\treturn series\n\t}\n\treturn jujuversion.SupportedLTS()\n}', 'nl': 'PreferredSeries returns the preferred series to use when a charm does not explicitly specify a series .'}
        ,{'code': 'func (si *SolrInterface) CoreAdmin() (*CoreAdmin, error) {\n\tca, err := NewCoreAdmin(si.conn.url.String())\n\tif err != nil {\n\t\treturn nil, err\n\t}\n\tca.SetBasicAuth(si.conn.username, si.conn.password)\n\treturn ca, nil\n}', 'nl': 'Return new instance of CoreAdmin with provided solrUrl and basic auth'}
    ],
    'ruby': [
        {'code': 'def todolists\n      active_response = Logan::Client.get "/projects/#{@id}/todolists.json"\n      lists_array = active_response.parsed_response.map do |h|\n        Logan::TodoList.new h.merge({ :project_id => @id })\n      end\n    end', 'nl': 'get active todo lists for this project from Basecamp API'}
        ,{'code': 'def connection(api, options = {})\n      connection_options = default_options(options)\n      connection_options.merge!(builder: stack(options.merge!(api: api)))\n      if options[:connection_options]\n        connection_options.deep_merge!(options[:connection_options])\n      end\n      if ENV[\'DEBUG\']\n        p "Connection options : \\n"\n        pp connection_options\n      end\n      Faraday.new(connection_options)\n    end', 'nl': 'Creates http connection'}
        ,{'code': 'def settings(&block)\n      @settings ||= setup\n      settings = instance_variable_defined?(:@namespace) ? @settings.get_value(@namespace) : @settings\n      if block_given?\n        block.arity == 0 ? settings.instance_eval(&block) : block.call(settings)\n      end\n      settings\n    end', 'nl': 'Loaded configuration stored in Settings class . Accepts + block + as parameter .'}
        ,{'code': 'def breadcrumbs\n      return unless show_breadcrumbs?\n      content_for(\n        :breadcrumbs,\n        content_tag(:ol, class: "breadcrumb") do\n          concat(content_tag(:li, link_to("Home", root_path)))\n          if can_view_resource_index?\n            concat(\n              content_tag(\n                :li, controller_link\n              )\n            )\n          end\n        end\n      )\n    end', 'nl': 'Render navigational information in the form of breadcrumbs'}
    ],
    'php': [
        {'code': 'protected function getAllowedQueryParameters()\n    {\n        $queryParameters = QueryService::getDefaultQueryParameters();\n        $customParameters = $this->getCustomQueryParameters();\n        if (is_array($customParameters) && count($customParameters) > 0) {\n            $queryParameters = array_merge($queryParameters, $customParameters);\n        }\n        return $queryParameters;\n    }', 'nl': 'Get the query parameters for the current controller'}
        ,{'code': "protected function getArrayValue($actual)\n    {\n        if (is_object($actual)) {\n            return get_object_vars($actual);\n        }\n        if (is_array($actual)) {\n            return $actual;\n        }\n        throw new \\InvalidArgumentException('KeysMatcher expects object or array');\n    }", 'nl': 'Normalize the actual value into an array whether it is an object or an array .'}
        ,{'code': 'public function drop($disconnect = false)\n    {\n        if ($disconnect) {\n            if ($this->valid()) {\n                $this->position = $this->size;\n                $this->connection->disconnect();\n            }\n        } else {\n            while ($this->valid()) {\n                $this->next();\n            }\n        }\n    }', 'nl': 'Drop queued elements that have not been read from the connection either by consuming the rest of the multibulk response or quickly by closing the underlying connection .'}
        ,{'code': 'public static function createFromBase(SymfonyUploadedFile $file, $test = false)\n    {\n        return $file instanceof static ? $file : new static(\n            $file->getPathname(),\n            $file->getClientOriginalName(),\n            $file->getClientMimeType(),\n            $file->getClientSize(),\n            $file->getError(),\n            $test\n        );\n    }', 'nl': 'Create a new file instance from a base instance .'}
    ],
    'erlang': [{'code': 'grow_heap(Config) when is_list(Config) ->\n    ct:timetrap({minutes, 40}),\n    ok  = grow_heap1(256),\n    ok  = grow_heap1(512),\n    ok  = grow_heap1(1024),\n    ok  = grow_heap1(2048),\n    ok.', 'nl': 'Produce a growing list of elements , for X calls , then drop one item per call until the list is empty .'}, {'code': 'do_set_up(S) when S#xref.mode =:= functions ->\n    ModDictList = dict:to_list(S#xref.modules),\n    [DefAt0, L, X0, LCallAt, XCallAt, CallAt, LC, XC, LU,\n     EE0, ECallAt, UC, LPredefined, OL,\n     Mod_DF,Mod_DF_1,Mod_DF_2,Mod_DF_3] = make_families(ModDictList, 19),\n    {XC_1, XU, XPredefined} = do_set_up_1(XC),\n    LC_1 = user_family(union_of_family(LC)),\n    E_1 = family_union(XC_1, LC_1),\n    Predefined = family_union(XPredefined, LPredefined),', 'nl': 'If data has been supplied using add_module / 9 ( and that is the only sanctioned way ) , then DefAt , L , X , LCallAt , XCallAt , CallAt , XC , LC , LU and OL are guaranteed to be functions ( with all supplied modules as domain ( disregarding unknown modules , that is , modules not supplied but hosting unknown functions ) ) .'}, {'code': 'prep_list_commands(E) ->\n    A = a0(),\n    substitute_v1(fun({value,Anno,_V}) ->\n                          CommandN = erl_anno:line(Anno),\n                          {call,A,{atom,A,v},[{integer,A,CommandN}]}\n                  end, E).', 'nl': 'Rather than listing possibly huge results the calls to v / 1 are shown .'}, {'code': 'find_app(Name, Vsn, Apps, LibDirs, CheckCodeLibDirs) ->\n    case maps:find(Name, Apps) of\n        {ok, AppInfo} ->\n            case check_app(Name, Vsn, AppInfo) of\n                true ->\n                    AppInfo;\n                false ->\n                    search_for_app(Name, Vsn, LibDirs, CheckCodeLibDirs)\n            end;\n        error ->\n            search_for_app(Name, Vsn, LibDirs, CheckCodeLibDirs)\n    end.', 'nl': "Applications are first searched for in the ` Apps ' variable which is a map of application name to `rlx_app_info' map ."}],
    'haskell': [{'code': 'stackTestSuiteFiles test =\n  resolveComponentFiles (CTest test.name.unqualCompToText) build names\n where\n  names = bnames <> exposed\n  exposed =\n    case test.interface of\n      TestSuiteExeV10 _ fp -> [DotCabalMain fp]\n      TestSuiteLibV09 _ mn -> [DotCabalModule mn]\n      TestSuiteUnsupported _ -> []\n  bnames = map DotCabalModule build.otherModules\n  build = test.buildInfo', 'nl': 'Get all files referenced by the test .'}, {'code': "unevalLits ast = do\n    lits <- foldJS (\\_ _ -> True) gatherLits S.empty ast\n    mapJS (const True) pure (pure . removeUpdate (`S.member` lits)) ast\n  where\n    gatherLits s (Stm (Assign (NewVar _ v) rhs _) _)\n      | definitelyNotThunk rhs         = pure $ S.insert v s\n      | Var v' <- rhs, v' `S.member` s = pure $ S.insert v s\n    gatherLits s _                     = pure s", 'nl': 'Eliminate evaluation of vars that are guaranteed not to be thunks .'}, {'code': 'mkFileHandle dev filepath iomode mb_codec tr_newlines = do\n   mkHandle dev filepath (ioModeToHandleType iomode) Nothing mb_codec\n            tr_newlines\n            (Just handleFinalizer) Nothing ', 'nl': "makes a new 'Handle' ."}, {'code': "unicl a = foldr unicl' [] a\n          where\n          unicl' p x = if tautclause cp then x else insert cp x\n                       where\n                       cp = clause p", 'nl': 'form unique clausal axioms excluding tautologies .'}],
    'prolog': [{'code': "'$lgt_mt_det_reply'(Queue, Goal, This, Self, Tag, Id) :-\n\tthread_get_message(Queue, '$lgt_reply'(Reply, This, Self, Tag, Result, Id)),\n\t(\tResult == success ->\n\t\tGoal = Reply\n\t;\tResult == failure ->\n\t\tfail\n\t;\tthrow(Result)\n\t).", 'nl': 'return the solution found .'}, {'code': "'$lgt_compile_head'(':'(Module, Head), ':'(Module, Functor/Arity), THead, _) :-\n\t!,\n\t'$lgt_check'(callable, Head),\n\tfunctor(Head, Functor, Arity),\n\t(\tModule == user ->\n\t\tTHead = Head\n\t;\t'$lgt_check'(module_identifier, Module),\n\t\tTHead = ':'(Module, Head)\n\t),\n\t(\tModule == user, '$lgt_pp_directive_'(multifile(Functor/Arity)) ->\n\t\ttrue\n\t;\t'$lgt_pp_directive_'(multifile(':'(Module, Functor/Arity))) ->\n\t\ttrue\n\t;\t'$lgt_pp_missing_multifile_directive_'(':'(Module,Functor/Arity), _, _) ->\n\t\ttrue\n\t;\t'$lgt_source_file_context'(File, Lines),\n\t\tassertz('$lgt_pp_missing_multifile_directive_'(':'(Module,Functor/Arity), File, Lines))\n\t).", 'nl': 'compile the head of a clause of a module predicate ( which we check if declared multifile ) .'}, {'code': "'$lgt_send_to_obj_rt'(Obj, Pred, Events, Ctx) :-\n\t'$lgt_comp_ctx_exec_ctx'(Ctx, ExCtx),\n\t'$lgt_check'(callable, Pred, logtalk(Obj::Pred, ExCtx)),\n\tcatch(\n\t\t'$lgt_compile_message_to_object'(Pred, Obj, TPred, Events, Ctx),\n\t\tError,\n\t\tthrow(error(Error, logtalk(Obj::Pred, ExCtx)))\n\t),\n\tcall(TPred).", 'nl': "'$lgt_send_to_obj_rt' ( ? term , ? term , + atom , + compilation_context ) runtime processing of a message sending call when the message and possibly the receiver object are not known at compile time ."}, {'code': "'$lgt_compile_bb_key'(Key, Prefix, TKey, Goal) :-\n\t(\tvar(Key) ->\n\t\tthrow(error(instantiation_error, Goal))\n\t;\tatomic(Key) ->\n\t\t'$lgt_compile_bb_key'(Key, Prefix, TKey)\n\t;\tthrow(error(type_error(atomic, Key), Goal))\n\t).", 'nl': "'$lgt_compile_bb_key' ( @ term , + atom , - atom , @ callable ) runtime translation of a blackboard key ."}]
}

fewshot_example_intent = {
    'what': [{'code': 'public static DefaultGoApiResponse incompleteRequest(String responseBody) {\n        DefaultGoApiResponse defaultGoApiResponse = new DefaultGoApiResponse(412);\n        defaultGoApiResponse.setResponseBody(responseBody);\n        return defaultGoApiResponse;\n    }', 'nl': 'Creates an instance DefaultGoApiResponse which represents incomplete request with response code 412'}, {'code': 'public OvhTask serviceName_partition_partitionName_quota_uid_DELETE(String serviceName, String partitionName, Long uid) throws IOException {\n\t\tString qPath = "/dedicated/nas/{serviceName}/partition/{partitionName}/quota/{uid}";\n\t\tStringBuilder sb = path(qPath, serviceName, partitionName, uid);\n\t\tString resp = exec(qPath, "DELETE", sb.toString(), null);\n\t\treturn convertTo(resp, OvhTask.class);\n\t}', 'nl': 'Delete a given quota'}, {'code': 'public static void setFileProperties (File fileNode) throws FrameworkException {\n\t\tfinal PropertyMap properties = new PropertyMap();\n\t\tString id = fileNode.getProperty(GraphObject.id);\n\t\tif (id == null) {\n\t\t\tfinal String newUuid = UUID.randomUUID().toString().replaceAll("[\\\\-]+", "");\n\t\t\tid = newUuid;\n\t\t\tfileNode.unlockSystemPropertiesOnce();\n\t\t\tproperties.put(GraphObject.id, newUuid);\n\t\t}\n\t\tfileNode.unlockSystemPropertiesOnce();\n\t\tfileNode.setProperties(fileNode.getSecurityContext(), properties);\n\t}', 'nl': 'Set the uuid and the path of a newly created fileNode'}, {'code': 'public boolean redo() {\n    LOGGER.trace("redo, before, size: " + changes.size() + " pos: " + position.get()\n        + " validPos: " + validPosition.get());\n    Change nextChange = next();\n    if (nextChange != null) {\n      doWithoutListeners(nextChange.getSetting(), nextChange::redo);\n      LOGGER.trace("redo, after, size: " + changes.size() + " pos: " + position.get()\n          + " validPos: " + validPosition.get());\n      return true;\n    }\n    return false;\n  }', 'nl': 'Redos a change in the history .'}],
    'why': [{'code': 'private void scheduleDriversForTaskLifeCycle()\n    {\n        List<DriverSplitRunner> runners = new ArrayList<>();\n        for (DriverSplitRunnerFactory driverRunnerFactory : driverRunnerFactoriesWithTaskLifeCycle) {\n            for (int i = 0; i < driverRunnerFactory.getDriverInstances().orElse(1); i++) {\n                runners.add(driverRunnerFactory.createDriverRunner(null, Lifespan.taskWide()));\n            }\n        }\n        enqueueDriverSplitRunner(true, runners);\n        for (DriverSplitRunnerFactory driverRunnerFactory : driverRunnerFactoriesWithTaskLifeCycle) {\n            driverRunnerFactory.noMoreDriverRunner(ImmutableList.of(Lifespan.taskWide()));\n            verify(driverRunnerFactory.isNoMoreDriverRunner());\n        }\n    }', 'nl': 'They also have a few differences making it more convenient to keep the two methods separate .'}, {'code': '@Override\n    public IDocumentSession openSession(String database) {\n        SessionOptions sessionOptions = new SessionOptions();\n        sessionOptions.setDatabase(database);\n        return openSession(sessionOptions);\n    }', 'nl': 'Opens the session for a particular database'}, {'code': 'public static iptunnel[] get(nitro_service service, iptunnel_args args) throws Exception{\n\t\tiptunnel obj = new iptunnel();\n\t\toptions option = new options();\n\t\toption.set_args(nitro_util.object_to_string_withoutquotes(args));\n\t\tiptunnel[] response = (iptunnel[])obj.get_resources(service, option);\n\t\treturn response;\n\t}', 'nl': 'Use this API to fetch all the iptunnel resources that are configured on netscaler . This uses iptunnel_args which is a way to provide additional arguments while fetching the resources .'}, {'code': 'public OvhOvhPabxDialplanExtensionRule billingAccount_ovhPabx_serviceName_dialplan_dialplanId_extension_extensionId_rule_POST(String billingAccount, String serviceName, Long dialplanId, Long extensionId, OvhOvhPabxDialplanExtensionRuleActionEnum action, String actionParam, Boolean negativeAction, Long position) throws IOException {\n\t\tString qPath = "/telephony/{billingAccount}/ovhPabx/{serviceName}/dialplan/{dialplanId}/extension/{extensionId}/rule";\n\t\tStringBuilder sb = path(qPath, billingAccount, serviceName, dialplanId, extensionId);\n\t\tHashMap<String, Object>o = new HashMap<String, Object>();\n\t\taddBody(o, "action", action);\n\t\taddBody(o, "actionParam", actionParam);\n\t\taddBody(o, "negativeAction", negativeAction);\n\t\taddBody(o, "position", position);\n\t\tString resp = exec(qPath, "POST", sb.toString(), o);\n\t\treturn convertTo(resp, OvhOvhPabxDialplanExtensionRule.class);\n\t}', 'nl': 'Create a new rule for an extension'}],
    'usage': [{'code': 'public void deleteRegisteredListeners(RESTRequest request, int clientID, ObjectName source_objName, JSONConverter converter) {\n        ClientNotificationArea clientArea = getInboxIfAvailable(clientID, null);\n        clientArea.removeAllListeners(request, source_objName, converter);\n    }', 'nl': 'Delete all registered server - side notifications for the given object name . This can only be called from HTTP - direct clients'}, {'code': 'protected ParsedResume parseResume(String url, Object requestPayLoad, Map<String, String> uriVariables) {\n        ParsedResume response = null;\n        for (int tryNumber = 1; tryNumber <= RESUME_PARSE_RETRY; tryNumber++) {\n            try {\n                response = this.performPostResumeRequest(url, requestPayLoad, uriVariables);\n                break;\n            } catch (HttpStatusCodeException error) {\n                response = handleResumeParseError(tryNumber, error);\n            } catch (Exception e) {\n                log.error("error", e);\n            }\n        }\n        return response;\n    }', 'nl': 'Makes the call to the resume parser . If parse fails this method will retry RESUME_PARSE_RETRY number of times .'}, {'code': 'public Object invoke (Object proxy, Method method, Object[] args) throws Throwable {\n        if (isCorrectMethod(method, args)) {\n            boolean handled = callTarget(args[0]);\n            setApplicationEventHandled(args[0], handled);\n        }\n        return null;\n    }', 'nl': 'This is the entry point for our proxy object ; it is called every time an ApplicationListener method is invoked'}, {'code': '@Override\n    public void show() {\n        final Stage stage = getStage();\n        stage.getRoot().clearChildren();\n        LmlUtilities.appendActorsToStage(stage, actors);\n    }', 'nl': 'Invoked after previous view is hidden and this view is about to show . Might be called when the view is being reloaded . Clears previous stage actors and adds managed actor to stage . If overridden call super .'}],
    'done': [{'code': 'public void remove(ValidationResultsModel validationResultsModel) {\n\t\tif (children.remove(validationResultsModel)) {\n\t\t\tvalidationResultsModel.removeValidationListener(this);\n\t\t\tvalidationResultsModel.removePropertyChangeListener(HAS_ERRORS_PROPERTY, this);\n\t\t\tvalidationResultsModel.removePropertyChangeListener(HAS_WARNINGS_PROPERTY, this);\n\t\t\tvalidationResultsModel.removePropertyChangeListener(HAS_INFO_PROPERTY, this);\n\t\t\tif (validationResultsModel.getMessageCount() > 0)\n\t\t\t\tfireChangedEvents();\n\t\t}\n\t}', 'nl': 'Remove the given validationResultsModel from the list of children . Remove listeners and if it had messages fire events .'}, {'code': 'public final long appendRecord(T record) throws IOException {\n\t\tlong pointer = this.writeView.getCurrentPointer();\n\t\ttry {\n\t\t\tthis.serializer.serialize(record, this.writeView);\n\t\t\tthis.recordCounter++;\n\t\t\treturn pointer;\n\t\t} catch (EOFException e) {\n\t\t\tthis.writeView.resetTo(pointer);\n\t\t\tthrow e;\n\t\t}\n\t}', 'nl': 'Inserts the given object into the current buffer . This method returns a pointer that can be used to address the written record in this partition .'}, {'code': 'public static void main(String[] args) throws IOException {\n\t\tApiOvhCore core = new ApiOvhCore();\n\t\tApiOvhCloud cloud = new ApiOvhCloud(core);\n\t\tArrayList<String> projects = cloud.project_GET();\n\t\tfor (String project: projects) {\n\t\t\tSystem.out.println(project);\n\t\t\tArrayList<OvhNetwork> networds = cloud.project_serviceName_network_private_GET(project);\n\t\t\tList<String> debug = networds.stream().map(ApiOvhUtils::objectJsonBody).collect(Collectors.toList());\n\t\t\tSystem.out.println(debug);\n\t\t}\n\t}', 'nl': 'Login using ovh . conf'}, {'code': 'private int s2i(final byte[] bytes) {\n    int num = 0;\n    for (int i = 0; i < 4; i++) {\n      num += (bytes[i] & 0xff) << ((3 - i) * 8);\n    }\n    return num;\n  }', 'nl': 'Read four bytes off the provided byte string and return the value as a big endian 32 bit unsigned integer .'}],
    'property': [{'code': '@Deprecated\r\n  public OIndex<?> getIndex() {\r\n    Set<OIndex<?>> indexes = owner.getInvolvedIndexes(name);\r\n    if (indexes != null && !indexes.isEmpty())\r\n      return indexes.iterator().next();\r\n    return null;\r\n  }', 'nl': 'Returns the first index defined for the property .'}, {'code': '@Override\n    public double get( int row , int col ) {\n        if( col < 0 || col >= numCols || row < 0 || row >= numRows ) {\n            throw new IllegalArgumentException("Specified element is out of bounds: "+row+" "+col);\n        }\n        return data[ row * numCols + col ];\n    }', 'nl': 'Returns the value of the specified matrix element . Performs a bounds check to make sure the requested element is part of the matrix .'}, {'code': 'protected double evalH(double f, double g) {\r\n    double h ;\r\n    h = 1.0 - Math.sqrt(f / g);\r\n    return h;\r\n  }', 'nl': 'Returns the value of the ZDT1 function H .'}, {'code': 'public Map<String, Deque<String>> getQueryParameters() {\n        if (queryParameters == null) {\n            queryParameters = new TreeMap<>();\n        }\n        return queryParameters;\n    }', 'nl': 'Returns a mutable map of query parameters .'}]
}


def generate_summaries_zero_shot(args, model, code, output_file, cnt=0):
    args.logger.info('zero-shot prompt...')

    f = open(output_file, args.mode, encoding="utf-8", newline='')
    writer = csv.writer(f)
    for idx, c in tqdm(enumerate(code)):
        if idx < cnt: continue
        message = model.ask(input=args.basic_prompt + c)
        writer.writerow([idx, message])
        print('current idx:', idx)
    f.close()


def generate_summaries_few_shot_history(args, model, code, output_file, cnt=0):  # few-shot example as history
    args.logger.info('few-shot hostory prompt...')
    history_prompt = []
    for example in args.fewshot_example:
        ex_code = example['code']
        nl = example['nl']
        history_prompt.append((args.basic_prompt + ex_code, nl))

    f = open(output_file, args.mode, encoding="utf-8", newline='')
    writer = csv.writer(f)
    for idx, c in tqdm(enumerate(code)):
        if idx < cnt: continue
        message = model.ask(input=args.basic_prompt + c, history=history_prompt)
        writer.writerow([idx, message])
        print('current idx:', idx)
    f.close()


def generate_summaries_chain_of_thought(args, model, code, output_file, cnt=0):
    args.logger.info('chain of thought prompt...')
    prompt1 = \
        '''Code:
        {}

        Question：
        1、What is the name of the function?
        2、What are the input parameters that are being accepted by the function?
        3、What is the expected output or return value of the function?
        4、Are there any specific requirements or constraints for using this function?
        5、Does the function have any additional dependencies or external requirements?
        Please Answer the above questions.'''
    prompt2 = 'Let\'s integrate the above information and generate a short comment in one sentence for the function.'
    f = open(output_file, args.mode, encoding="utf-8", newline='')
    writer = csv.writer(f)
    for idx, c in tqdm(enumerate(code)):
        if idx < cnt: continue
        reply1 = model.ask(input=prompt1.format(c))
        message = model.ask(input=prompt2, history=[(prompt1.format(c), reply1)])
        writer.writerow([idx, message])
        print('current idx:', idx)
    f.close()


def generate_summaries_critique(args, model, code, output_file, cnt=0):
    args.logger.info('critique prompt...')
    prompt2 = 'Review your previous answer and find problems with your answer.'
    prompt3 = 'Based on the problems you found, improve your answer.'

    f = open(output_file, args.mode, encoding="utf-8", newline='')
    writer = csv.writer(f)
    for idx, c in tqdm(enumerate(code)):
        if idx < cnt: continue
        reply1 = model.ask(input=args.basic_prompt + c)
        reply2 = model.ask(input=prompt2, history=[(args.basic_prompt + c, reply1)])
        message = model.ask(input=prompt3, history=[(args.basic_prompt + c, reply1), (prompt2, reply2)])
        writer.writerow([idx, message])
        print('current idx:', idx)
    f.close()


def generate_summaries_expert_history(args, model, code, output_file, cnt=0):
    args.logger.info('expert history prompt...')
    expert_prompt = 'For the following instruction, write a high-quality description about the most capable and suitable agent to answer the instruction in second person perspective:\n'

    expert_example = [{'Instruction': 'Make a list of 5 possible effects of deforestation.',
                       'Description': 'You are an environmental scientist with a specialization in the study of ecosystems and their interactions with human activities. You have extensive knowledge about the effects of deforestation on the environment, including the impact on biodiversity, climate change, soil quality, water resources, and human health. Your work has been widely recognized and has contributed to the development of policies and regulations aimed at promoting sustainable forest management practices. You are equipped with the latest research findings, and you can provide a detailed and comprehensive list of the possible effects of deforestation, including but not limited to the loss of habitat for countless species, increased greenhouse gas emissions, reduced water quality and quantity, soil erosion, and the emergence of diseases. Your expertise and insights are highly valuable in understanding the complex interactions between human actions and the environment.'
                       }, {'Instruction': 'Identify a descriptive phrase for an eclipse.',
                           'Description': 'You are an astronomer with a deep understanding of celestial events and phenomena. Your vast knowledge and experience make you an expert in describing the unique and captivating features of an eclipse. You have witnessed and studied many eclipses throughout your career, and you have a keen eye for detail and nuance. Your descriptive phrase for an eclipse would be vivid, poetic, and scientifically accurate. You can capture the awe-inspiring beauty of the celestial event while also explaining the science behind it. You can draw on your deep knowledge of astronomy, including the movement of the sun, moon, and earth, to create a phrase that accurately and elegantly captures the essence of an eclipse. Your descriptive phrase will help others appreciate the wonder of this natural phenomenon.'
                           },
                      {'Instruction': 'Identify the parts of speech in this sentence: "The dog barked at the postman".',
                       'Description': 'You are a linguist, well-versed in the study of language and its structures. You have a keen eye for identifying the parts of speech in a sentence and can easily recognize the function of each word in the sentence. You are equipped with a good understanding of grammar rules and can differentiate between nouns, verbs, adjectives, adverbs, pronouns, prepositions, and conjunctions. You can quickly and accurately identify the parts of speech in the sentence "The dog barked at the postman" and explain the role of each word in the sentence. Your expertise in language and grammar is highly valuable in analyzing and understanding the nuances of communication.'
                       }]
    history_prompt = []
    for example in expert_example:
        ex_ins = example['Instruction']
        ex_des = example['Description']
        history_prompt.append((expert_prompt + ex_ins, ex_des))
    system_prompt = model.ask(expert_prompt + 'Generate a short comment in one sentence for a function.', history=history_prompt, system_prompt='You are a helpful assistant.')

    f = open(output_file, args.mode, encoding="utf-8", newline='')
    writer = csv.writer(f)
    for idx, c in tqdm(enumerate(code)):
        if idx < cnt: continue
        message = model.ask(input=args.basic_prompt + c, system_prompt=system_prompt)
        writer.writerow([idx, message])
        print('current idx:', idx)
    f.close()



def write_ground_truth(gold, output_path):
    f = open(output_path, "w", encoding="utf-8", newline='')
    writer = csv.writer(f)
    cnt = 0
    for g in tqdm(gold):
        writer.writerow([cnt, g])
        cnt = cnt + 1
    f.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--openai_key", required=True, type=str)

    parser.add_argument("--data_file", default="./dataset/java.jsonl", type=str)
    parser.add_argument("--language", default="java", type=str)
    parser.add_argument("--model", default="gpt-3.5", type=str)
    parser.add_argument("--count", default=0, type=int, help="continue from sample `count`")

    parser.add_argument("--temperature", default=0.1, type=float)
    parser.add_argument("--top_p", default=1.0, type=float)

    parser.add_argument("--intent", default=False, type=bool)  # True: use fewshot_example_intent, False: use fewshot_example_language_4
    parser.add_argument("--intent_type", default='', type=str)  # only used when intent is True

    parser.add_argument("--write_groundtruth", default=False, type=bool)

    parser.add_argument("--max_new_tokens", default=4096, type=int)
    parser.add_argument("--top_k", default=50, type=int)
    parser.add_argument("--basic_prompt", default='Please generate a short comment in one sentence for the following function:\n', type=str)
    parser.add_argument("--log_filename", default='log.txt', type=str)
    args = parser.parse_args()

    # ouput directory
    if args.intent:
        dir = './result/{}/{}/{}/{}/'.format(args.intent_type, args.model, args.temperature, args.top_p)
        if os.path.exists(dir) == False:
            os.makedirs(dir)
    else:
        dir = './result/{}/{}/{}/{}/'.format(args.language, args.model, args.temperature, args.top_p)
        if os.path.exists(dir) == False:
            os.makedirs(dir)

    # logger
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    args.logger = logging.getLogger(__name__)
    log_file_path = os.path.join(os.path.join(dir, args.log_filename))
    fh = logging.FileHandler(log_file_path)
    args.logger.addHandler(fh)  # add the handlers to the logger
    args.logger.info("Training/evaluation parameters %s", args)
    args.logger.info("\n")

    # load data
    code = []
    gold = []
    if args.language == 'c':
        with open(args.data_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                js = json.loads(line)
                code.append(remove_comments_and_docstrings(source=js['function'], lang=args.language))
                comment = js['summary']
                if comment.endswith('.'):
                    comment = comment[:-1]
                comment = comment + ' .'
                gold.append(comment)
    else:
        with open(args.data_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                js = json.loads(line)
                code.append(remove_comments_and_docstrings(source=js['code'], lang=args.language))
                gold.append(' '.join(js['docstring_tokens']))

    # load fewshot_example
    # args.fewshot_example = fewshot_example_language_3[args.language]
    if args.intent:
        args.fewshot_example = fewshot_example_intent[args.intent_type]
    else:
        args.fewshot_example = fewshot_example_language_4[args.language]

    # load model
    MODEL_NAME_OR_PATH = {'gpt-4':'gpt-4-1106-preview',
                          'gpt-3.5':'gpt-3.5-turbo',
                          'starchat': '/home/david/MY/llm/starchat',
                         'codellama':'/home/david/MY/codellama/CodeLlama-7b-Instruct-hf',
                          }
    args.model_name_or_path = MODEL_NAME_OR_PATH[args.model]
    if args.model == 'gpt-4':
        model = GPT(args=args)
    elif args.model == 'gpt-3.5':
        model = GPT(args=args)
    elif args.model == 'starchat':
        model = StarChat(args=args)
    elif args.model == 'codellama':
        model = CodeLLAMA(args=args)
    else:
        print('Model not found!')
        sys.exit(1)

    # write ground truth
    if args.write_groundtruth:
        if args.intent:
            write_ground_truth(gold, './result/{}/groundtruth.csv'.format(args.intent_type))
        else:
            write_ground_truth(gold, './result/{}/groundtruth.csv'.format(args.language))

    if args.count > 0:
        args.mode = 'a'
    else:
        args.mode = 'w'

    # prompt
    generate_summaries_zero_shot(args, model, code, dir + 'zero_shot.csv', args.count)
    generate_summaries_few_shot_history(args, model, code, dir + 'few_shot_history_4.csv', args.count)
    generate_summaries_expert_history(args, model, code, dir + 'expert_history.csv', args.count)

    generate_summaries_chain_of_thought(args, model, code, dir + 'chain_of_thought.csv', args.count)
    generate_summaries_critique(args, model, code, dir + 'critique.csv', args.count)


if __name__ == '__main__':
    os.environ["http_proxy"] = "http://127.0.0.1:10809"
    os.environ["https_proxy"] = "http://127.0.0.1:10809"

    main()
