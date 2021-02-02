from pqueens.utils.run_subprocess import run_subprocess
from pqueens.external_geometry.external_geometry import ExternalGeometry
import re
import fileinput
import numpy as np
import os


class BaciDatExternalGeometry(ExternalGeometry):
    """
    Class to read in external geometries based on BACI-dat files.

    Args:
        path_to_dat_file (str): Path to dat file from which the external_geometry_obj should be
                                extracted
        list_geometric_sets (list): List of geometric sets that should be extracted
        node_topology (lst): List with topology dicts of edges/nodes (here: mesh nodes not FEM
                             nodes) for each geometric set of this category
        line_topology (lst): List with topology dicts of line components for each geometric set
                             of this category
        surface_topology (lst): List of topology dicts of surfaces for each geometric set of this
                                category
        volume_topology (lst): List of topology of volumes for each geometric set of this category
        node_coordinates (lst): Dictionary of coordinates of mesh nodes

    Attributes:
        path_to_dat_file (str): Path to dat file from which the external_geometry_obj should be
                                extracted
        list_geometric_sets (lst): List of geometric sets that should be extracted
        current_dat_section (str): String that encodes the current section in the dat file as
                                   file is read line-wise
        design_description (dict): First section of the dat-file as dictionary to summarize the
                                   external_geometry_obj components
        node_topology (lst): List with topology dicts of edges/nodes (here: mesh nodes not FEM
                             nodes) for each geometric set of this category
        line_topology (lst): List with topology dicts of line components for each geometric set
                             of this category
        surface_topology (lst): List of topology dicts of surfaces for each geometric set of this
                                category
        volume_topology (lst): List of topology of volumes for each geometric set of this category
        desired_dat_sections (dict): Dictionary that holds only desired dat-sections and
                                     geometric sets within these sections so that we can skip
                                     undesired parts of the dat-file
        nodes_of_interest (lst): List that contains all (mesh) nodes that are part of a desired
                                  geometric component
        node_coordinates (dict): Dictionary that holds the desired nodes as well as their
                                 corresponding geometric coordinates
        new_nodes_lst (lst): List of new nodes that should be written in dnode topology
        random_dirich_flag (bool): Flag to check if a random Dirichlet BC exists
        random_transport_dirich_flag (bool): Flag to check if a random transport Dirichlet BC exists
        random_neumann_flag (bool): Flag to check if a random Neumann BC exists
        nodes_written (bool): Flag to check whether nodes have already been written


    Returns:
        geometry_obj (obj): Instance of BaciDatExternalGeometry class

    """

    dat_sections = [
        'DESIGN DESCRIPTION',
        'DESIGN POINT DIRICH CONDITIONS',
        'DESIGN POINT TRANSPORT DIRICH CONDITIONS',
        'DNODE-NODE TOPOLOGY',
        'DLINE-NODE TOPOLOGY',
        'DSURF-NODE TOPOLOGY',
        'DVOL-NODE TOPOLOGY',
        'NODE COORDS',
    ]
    section_match_dict = {
        "DNODE": "DNODE-NODE TOPOLOGY",
        "DLINE": "DLINE-NODE TOPOLOGY",
        "DSURFACE": "DSURF-NODE TOPOLOGY",
        "DVOL": "DVOL-NODE TOPOLOGY",
    }

    def __init__(
        self,
        path_to_dat_file,
        list_geometric_sets,
        node_topology,
        line_topology,
        surface_topology,
        volume_topology,
        node_coordinates,
    ):

        super(BaciDatExternalGeometry, self).__init__()
        self.path_to_dat_file = path_to_dat_file
        self.list_geometric_sets = list_geometric_sets
        self.current_dat_section = None
        self.design_description = {}
        self.node_topology = node_topology
        self.line_topology = line_topology
        self.surface_topology = surface_topology
        self.volume_topology = volume_topology
        self.desired_dat_sections = {}
        self.nodes_of_interest = None
        self.node_coordinates = node_coordinates

        # some attributes for dat-file manipulation
        self.new_nodes_lst = None

        # some flags to memorize which sections have been written / manipulated
        self.random_dirich_flag = False
        self.random_transport_dirich_flag = False
        self.random_neumann_flag = False
        self.nodes_written = False

    @classmethod
    def from_config_create_external_geometry(cls, config):
        """
        Create BaciDatExternalGeometry object from problem description

        Args:
            config (dict): Problem description

        Returns:
            geometric_obj (obj): Instance of BaciDatExternalGeometry

        """
        interface_name = config['model'].get('interface')
        driver_name = config[interface_name].get('driver')
        path_to_dat_file = config[driver_name]['driver_params']['input_template']
        list_geometric_sets = config['external_geometry'].get('list_geometric_sets')
        node_topology = [{"node_mesh": [], "node_topology": [], "topology_name": ""}]
        line_topology = [{"node_mesh": [], "line_topology": [], "topology_name": ""}]
        surface_topology = [{"node_mesh": [], "surface_topology": [], "topology_name": ""}]
        volume_topology = [{"node_mesh": [], "volume_topology": [], "topology_name": ""}]
        node_coordinates = {"node_mesh": [], "coordinates": []}

        return cls(
            path_to_dat_file,
            list_geometric_sets,
            node_topology,
            line_topology,
            surface_topology,
            volume_topology,
            node_coordinates,
        )

    # --------------- child methods that must be implemented --------------------------------------
    def read_external_data(self):
        """Read the external input file with geometric data"""
        self._read_geometry_from_dat_file()

    def organize_sections(self):
        """Organize the sections of the external external_geometry_obj"""
        self._get_desired_dat_sections()

    def finish_and_clean(self):
        """Finish and clean the analysis for external external_geometry_obj extraction"""
        self._sort_node_coordinates()

    # -------------- helper methods ---------------------------------------------------------------
    def _read_geometry_from_dat_file(self):
        """
        Read the dat-file line by line to be memory efficient.
        Only save desired information.

        Returns:
            None

        """
        with open(self.path_to_dat_file) as my_dat:
            # read dat file line-wise
            for line in my_dat:
                line = line.strip()

                match_bool = self._get_current_dat_section(line)
                # skip comments outside of section definition
                if line[0:2] == '//' or match_bool:
                    pass
                else:
                    self._get_design_description(line)
                    self._get_only_desired_topology(line)
                    self._get_only_desired_coordinates(line)

    def _get_current_dat_section(self, line):
        """
        Check if the current line starts a new section in the dat-file.
        Update self.current_dat_section if new section was found. If the current line is the
        actual section identifier, return a True boolean.

        Args:
            line (str): Current line of the dat-file

        Returns:
            bool (boolean): True or False depending if current line is the section match

        """
        # regex for the sections
        section_name_re = re.compile('^-+([^-].+)$')
        match = section_name_re.match(line)
        # get the current section of the dat file
        if match:
            # remove whitespaces and horizontal line
            section_string = line.strip('-')
            section_string = section_string.strip()
            # check for comments
            if line[:2] == '//':
                return True
            # ignore comment pattern after actual string
            elif section_string.strip('//') in self.dat_sections:
                self.current_dat_section = section_string
                return True
            else:
                self.current_dat_section = None
                return True
        else:
            return False

    def _check_if_in_desired_dat_section(self):
        """
        Return True if we are in a dat-section that contains the desired geometric set.

        Returns:
            Boolean

        """
        if self.current_dat_section in self.desired_dat_sections.keys():
            return True
        else:
            return False

    def _get_desired_dat_sections(self):
        """
        Get the dat-sections (and its identifier) that contain the desired geometric sets.

        Returns:
            None

        """
        # initialize keys with empty lists
        for geo_set in self.list_geometric_sets:
            self.desired_dat_sections[self.section_match_dict[geo_set.split()[0]]] = []

        # write desired geometric set to corresponding section key
        for geo_set in self.list_geometric_sets:
            self.desired_dat_sections[self.section_match_dict[geo_set.split()[0]]].append(geo_set)

    def _get_topology(self, line):
        """
        Get the geometric topology by extracting and grouping (mesh) nodes that
        belong to the desired geometric sets and save them to their topology class.

        Args:
            line (str): Current line of the dat-file

        Returns:
            None

        """
        topology_name = ' '.join(line.split()[2:4])
        node_list = line.split()
        # get edges
        if self.current_dat_section == 'DNODE-NODE TOPOLOGY':
            if topology_name in self.desired_dat_sections['DNODE-NODE TOPOLOGY']:
                if (self.node_topology[-1]['topology_name'] == "") or (
                    self.node_topology[-1]['topology_name'] == topology_name
                ):
                    self.node_topology[-1]['node_mesh'].append(int(node_list[1]))
                    self.node_topology[-1]['node_topology'].append(int(node_list[3]))
                    self.node_topology[-1]['topology_name'] = topology_name
                else:
                    new_node_topology_dict = {
                        'node_mesh': int(node_list[1]),
                        'node_topology': int(node_list[3]),
                        'topology_name': topology_name,
                    }
                    self.node_topology.extend(new_node_topology_dict)

        # get lines
        elif self.current_dat_section == 'DLINE-NODE TOPOLOGY':
            if topology_name in self.desired_dat_sections['DLINE-NODE TOPOLOGY']:
                if (self.line_topology[-1]['topology_name'] == "") or (
                    self.line_topology[-1]['topology_name'] == topology_name
                ):
                    self.line_topology[-1]['node_mesh'].append(int(node_list[1]))
                    self.line_topology[-1]['line_topology'].append(int(node_list[3]))
                    self.line_topology[-1]['topology_name'] = topology_name
                else:
                    new_line_topology_dict = {
                        'node_mesh': int(node_list[1]),
                        'line_topology': int(node_list[3]),
                        'topology_name': topology_name,
                    }
                    self.line_topology.extend(new_line_topology_dict)

        # get surfaces
        elif self.current_dat_section == 'DSURF-NODE TOPOLOGY':
            if topology_name in self.desired_dat_sections['DSURF-NODE TOPOLOGY']:
                # append points to last list entry if geometric set is the name
                if (self.surface_topology[-1]['topology_name'] == "") or (
                    self.surface_topology[-1]['topology_name'] == topology_name
                ):
                    self.surface_topology[-1]['node_mesh'].append(int(node_list[1]))
                    self.surface_topology[-1]['surface_topology'].append(int(node_list[3]))
                    self.surface_topology[-1]['topology_name'] = topology_name

                # extend list with new geometric set
                else:
                    new_surf_topology_dict = {
                        'node_mesh': int(node_list[1]),
                        'surface_topology': int(node_list[3]),
                        'topology_name': topology_name,
                    }
                    self.surface_topology.extend(new_surf_topology_dict)

        # get volumes
        elif self.current_dat_section == 'DVOL-NODE TOPOLOGY':
            if topology_name in self.desired_dat_sections['DVOL-NODE TOPOLOGY']:
                # append points to last list entry if geometric set is the name
                if (self.volume_topology[-1]['topology_name'] == "") or (
                    self.volume_topology[-1]['topology_name'] == topology_name
                ):
                    self.volume_topology[-1]['node_mesh'].append(int(node_list[1]))
                    self.volume_topology[-1]['volume_topology'].append(int(node_list[3]))
                    self.volume_topology[-1]['topology_name'] = topology_name
                else:
                    new_volume_topology_dict = {
                        'node_mesh': int(node_list[1]),
                        'surface_topology': int(node_list[3]),
                        'topology_name': topology_name,
                    }
                    self.volume_topology.extend(new_volume_topology_dict)

    def _get_design_description(self, line):
        """
        Extract a short geometric description from the dat-file

        Args:
            line (str): Current line of the dat-file

        Returns:
            None

        """
        # get the overall design description of the problem at hand
        if self.current_dat_section == 'DESIGN DESCRIPTION':
            design_list = line.split()
            if len(design_list) != 2:
                raise IndexError(
                    f'Unexpected number of list entries in design '
                    f'description! The '
                    'returned list should have length 2 but the returned '
                    'list was {design_list}.'
                    'Abort...'
                )

            self.design_description[design_list[0]] = design_list[1]

    def _get_only_desired_topology(self, line):
        """
        Check if the current dat-file sections contains desired geometric sets. Skip the topology
        extraction if the current section does not contain a desired geometric set, anyways.

        Args:
            line (str): Current line of the dat-file

        Returns:
            None

        """
        # skip lines that are not part of a desired section
        desired_section_boolean = self._check_if_in_desired_dat_section()

        if not desired_section_boolean:
            pass
        else:
            # get topology groups
            self._get_topology(line)

    def _get_only_desired_coordinates(self, line):
        """
        Get coordinates of nodes that belong to a desired geometric set.

        Args:
            line (str): Current line of the dat-file

        Returns:
            None

        """
        if self.current_dat_section == 'NODE COORDS':
            node_list = line.split()
            if self.nodes_of_interest is None:
                self._get_nodes_of_interest()

            if self.nodes_of_interest is not None:
                if int(node_list[1]) in self.nodes_of_interest:
                    self._get_coordinates_of_desired_geometric_sets(node_list)

    def _get_coordinates_of_desired_geometric_sets(self, node_list):
        """
        Extract node and coordinate information of the current dat-file line.

        Args:
            node_list (list): Current line of the dat-file

        Returns:
            None

        """
        self.node_coordinates['node_mesh'].append(int(node_list[1]))
        nodes_as_float_list = [float(value) for value in node_list[3:6]]
        self.node_coordinates['coordinates'].append(nodes_as_float_list)

    def _get_nodes_of_interest(self):
        """
        Based on the extracted topology, get a unique list of all (mesh) nodes that are part of
        the extracted topology.

        Returns:
            None

        """
        node_mesh_nodes = []
        for node_topo in self.node_topology:
            node_mesh_nodes.extend(node_topo['node_mesh'])

        line_mesh_nodes = []
        for line_topo in self.line_topology:
            line_mesh_nodes.extend(line_topo['node_mesh'])

        surf_mesh_nodes = []
        for surf_topo in self.surface_topology:
            surf_mesh_nodes.extend(surf_topo['node_mesh'])

        vol_mesh_nodes = []
        for vol_topo in self.volume_topology:
            vol_mesh_nodes.extend(vol_topo['node_mesh'])

        nodes_of_interest = node_mesh_nodes + line_mesh_nodes + surf_mesh_nodes + vol_mesh_nodes

        # make node_list unique
        self.nodes_of_interest = list(set(nodes_of_interest))

    def _sort_node_coordinates(self):
        self.node_coordinates['coordinates'] = [
            coord
            for _, coord in sorted(
                zip(self.node_coordinates['node_mesh'], self.node_coordinates['coordinates']),
                key=lambda pair: pair[0],
            )
        ]
        self.node_coordinates['node_mesh'] = sorted(self.node_coordinates['node_mesh'])

    # -------------- write random fields to dat file ----------------------------------------------
    def write_random_fields_to_dat(self, random_fields_lst):
        """
        Write the realized random fields to the dat file/overwrite the old problem description

        Args:
            random_fields_lst (lst): List of descriptions for involved random fields whose
                                    field_realizations should be written to the dat-file

        Returns:
            new_dat_file_path (str): Path to the new dat-file template containing one realization of
                                     the random fields

        """
        # copy the dat file and rename it for the current simulation
        filename, file_extension = os.path.splitext(self.path_to_dat_file)
        new_dat_file_path = filename + "_copy" + file_extension
        cmd_lst = ['/bin/cp -rf', self.path_to_dat_file, new_dat_file_path]
        command_string = ' '.join(cmd_lst)
        _, _, _, stderr = run_subprocess(command_string)

        # this has to be done outside of the file read as order is not known a priori
        self._create_new_node_sets(random_fields_lst)

        if stderr:
            raise RuntimeError(
                f"Copying of simulation input file failed with error message: {stderr}"
            )

        # random_fields_lst is here a list containing a dict description per random field
        with fileinput.input(new_dat_file_path, inplace=True, backup='.bak') as my_dat:
            # read dat file line-wise
            for line in my_dat:
                old_line = line
                line = line.strip()

                match_bool = self._get_current_dat_section(line)
                # skip comments outside of section definition
                if line[0:2] == '//' or match_bool:
                    print(old_line, end='')
                else:
                    # check if in design description and if so extend it
                    if self.current_dat_section == 'DESIGN DESCRIPTION':
                        self._write_update_design_description(old_line, random_fields_lst)

                    # check if in sec. DNODE-NODE topology and if so adjust this section in case
                    # of random BCs; write this only once
                    elif (
                        self.current_dat_section == 'DNODE-NODE TOPOLOGY' and not self.nodes_written
                    ):
                        self._write_new_node_sets()
                        self.nodes_written = True
                        # print the current line that was overwritten
                        print(old_line, end='')

                    # check if in sec. for random dirichlet cond. and if point dirich exists extend
                    elif (
                        self.current_dat_section == 'DESIGN POINT DIRICH CONDITIONS'
                        and not self.random_dirich_flag
                    ):
                        self._write_design_point_dirichlet_conditions(random_fields_lst, line)
                        self.random_dirich_flag = True

                    elif (
                        self.current_dat_section == 'DESIGN POINT TRANSPORT DIRICH CONDITIONS'
                        and not self.random_transport_dirich_flag
                    ):
                        self._write_design_point_dirichlet_transport_conditions()
                        self.random_transport_dirich_flag = True

                    elif (
                        self.current_dat_section == 'DESIGN POINT NEUM'
                        and not self.random_neumann_flag
                    ):
                        self._write_design_point_neumann_conditions()
                        self.random_neumann_flag = True

                    # materials and elements / constitutive random fields -----------------------
                    elif self.current_dat_section == 'STRUCTURE ELEMENTS':
                        self._assign_elementwise_material_to_structure_ele()

                    elif self.current_dat_section == 'FLUID ELEMENTS':
                        raise NotImplementedError()

                    elif self.current_dat_section == 'ALE ELEMENTS':
                        raise NotImplementedError()

                    elif self.current_dat_section == 'TRANSPORT ELEMENTS':
                        raise NotImplementedError()

                    elif self.current_dat_section == 'MATERIALS':
                        # TODO not yet implemented
                        self._write_elementwise_stuct_materials()
                        self._write_elementwise_fluid_materials()
                        self._write_elementwise_transport_materials()
                        self._write_elementwise_ale_materials()

                    # If end of dat file is reached but certain sections did not exist so far,
                    # write them now
                    elif self.current_dat_section == 'END':
                        bcs_list = [
                            random_field["external_definition"]["type"]
                            for random_field in random_fields_lst
                        ]
                        if ('dirichlet' in bcs_list) and (self.random_dirich_flag is False):
                            print(
                                '----------------------------------------------DESIGN POINT '
                                'DIRICH CONDITIONS\n'
                            )
                            self._write_design_point_dirichlet_conditions(line)

                        elif ('transport_dirichlet' in bcs_list) and (
                            self.random_transport_dirich_flag is False
                        ):
                            print(
                                '----------------------------------------------DESIGN POINT '
                                'TRANSPORT DIRICH CONDITIONS\n'
                            )
                            self._write_design_point_dirichlet_transport_conditions()

                        elif ('neumann' in bcs_list) and (self.random_neumann_flag is False):
                            print(
                                '---------------------------------------------DESIGN POINT '
                                'NEUMANN CONDITIONS\n'
                            )
                            self._write_design_point_neumann_conditions()
                        # pylint: disable=line-too-long
                        print(
                            '-------------------------------------------------------------------------END\n'
                        )
                        # pylint: enable=line-too-long
                    else:
                        print(old_line, end='')

        return new_dat_file_path

    def _write_elementwise_stuct_materials(self):
        pass

    def _write_elementwise_fluid_materials(self):
        pass

    def _write_elementwise_transport_materials(self):
        pass

    def _write_elementwise_ale_materials(self):
        pass

    def _write_design_point_dirichlet_transport_conditions(self):
        pass

    def _write_design_point_neumann_conditions(self):
        pass

    def _assign_elementwise_material_to_structure_ele(self):
        pass

    def _write_update_design_description(self, old_line, random_fields_lst):
        """
        Overwrite the design description in the dat-file such that the new random field BCs are
        considered.

        Args:
            old_line (str): Current/former line in the dat-file
            random_fields_lst: List containing descriptions of random fields

        Returns:
            None

        """
        # Some clean-up of the line string
        line = old_line.strip()
        line_lst = line.split()
        additional_nodes = 0

        if line_lst[0] == "NDPOINT":
            # get random fields that are either Dirichlet or Neumann BCs
            for random_field in random_fields_lst:
                if (
                    (random_field["external_definition"]["type"] == "dirichlet")
                    or (random_field["external_definition"]["type"] == "neumann")
                    or (random_field["external_definition"]["type"] == "transport_dirichlet")
                ):
                    geometric_set_name = random_field["external_definition"]["external_instance"]
                    geo_set_name_type = geometric_set_name.split()[0]

                    my_topology = self._get_my_topology(geo_set_name_type)

                    # find set name in list of node topology and return number of nodes
                    if my_topology is not None:
                        set_nodes = np.sum(
                            [
                                len(node_set["node_mesh"])
                                for node_set in my_topology
                                if node_set['topology_name'] == geometric_set_name
                            ]
                        )
                    else:
                        raise ValueError(f"The topology '{my_topology}' is unknown. Abort...")

                    additional_nodes += set_nodes

            # add the nodes to the existing NDPOINTS
            number_string = str(int(line_lst[1]) + int(additional_nodes))

            # overwrite the dat entry
            print(f"NDPOINT                         {number_string}")

        else:
            print(old_line, end='')

    def _write_random_material_field(self):
        raise NotImplementedError()

    def _write_design_point_dirichlet_conditions(self, realized_random_fields_lst, line):
        """
        Convert the random fields, defined on the geometric set of interest, into design point
        dirichlet BCs such that each dpoint contains a discrete value of the random field

        Args:
            realized_random_fields_lst (lst): List containing the design description of the
                                              involved random fields
            line (str): String for the current line in the dat-file that is read in

        Returns:
            None

        """
        old_num = BaciDatExternalGeometry._get_old_num_design_point_dirichlet_conditions(line)
        self._overwrite_num_design_point_dirichlet_conditions(realized_random_fields_lst, old_num)
        # random fields for these sets if dirichlet
        for geometric_set in self.list_geometric_sets:
            fields_dirich_on_geo_set = [
                field
                for field in realized_random_fields_lst
                if (field["external_definition"]["type"] == "dirichlet")
                and (field["external_definition"]["external_instance"] == geometric_set)
            ]

            # select correct node set
            node_set = [
                node_set for node_set in self.new_nodes_lst if node_set["name"] == geometric_set
            ][0]

            # assign random dirichlet fields
            (
                realized_random_field_1,
                realized_random_field_2,
                realized_random_field_3,
                fun_1,
                fun_2,
                fun_3,
            ) = BaciDatExternalGeometry._assign_random_dirichlet_fields_per_geo_set(
                fields_dirich_on_geo_set
            )

            # take care of remaining deterministic dofs on the geometric set
            # we take the first field to get deterministic dofs
            (
                realized_random_field_1,
                realized_random_field_2,
                realized_random_field_3,
                fun_1,
                fun_2,
                fun_3,
            ) = BaciDatExternalGeometry._assign_deterministic_dirichlet_fields_per_geo_set(
                fields_dirich_on_geo_set,
                realized_random_field_1,
                realized_random_field_2,
                realized_random_field_3,
                fun_1,
                fun_2,
                fun_3,
            )

            # write the new fields to the dat file --------------------------------------------
            for topo_node, rf1, rf2, rf3, f1, f2, f3 in zip(
                node_set['topo_dnodes'],
                realized_random_field_1,
                realized_random_field_2,
                realized_random_field_3,
                fun_1,
                fun_2,
                fun_3,
            ):
                print(
                    f"E {topo_node} - NUMDOF 3 ONOFF 1 1 1 VAL {rf1} "
                    f"{rf2} {rf3} FUNCT {int(f1)} {int(f2)} {int(f3)}"
                )

    @staticmethod
    def _get_old_num_design_point_dirichlet_conditions(line):
        """
        Return the former number of dirichlet point conditions

        Args:
            line (str): String of current dat-file line

        Returns:
            old_num (int): old number of dirichlet point conditions

        """
        old_num = int(line.split()[1])

        return old_num

    def _overwrite_num_design_point_dirichlet_conditions(self, realized_random_fields_lst, old_num):
        """
        Write the new number of design point dirichlet conditions to the design description.

        Args:
            realized_random_fields_lst (lst): List containing vectors with the values of the
                                              realized random fields
            old_num (int): Former number of design point Dirichlet conditions

        Returns:
            None

        """
        # loop over all dirichlet nodes
        field_values = []
        for geometric_set in self.list_geometric_sets:
            field_values.extend(
                [
                    list(field['values'])
                    for field in realized_random_fields_lst
                    if (field["external_definition"]["type"] == "dirichlet")
                    and (field["external_definition"]["external_instance"] == geometric_set)
                ]
            )

        num_new_dpoints = len(field_values[0])
        num_existing_dpoints = old_num
        total_num_dpoints = num_new_dpoints + num_existing_dpoints
        print(f'DPOINT                          {total_num_dpoints}')

    @staticmethod
    def _assign_random_dirichlet_fields_per_geo_set(fields_dirich_on_geo_set):
        """


        Args:
            fields_dirich_on_geo_set (lst): List containing the descriptions and a
                                            realization of the Dirichlet BCs random fields.

        Returns:
            realized_random_field_1 (np.array): Array containing values of the random field (each
                                                row is associated to a corresponding row in the
                                                coordinate matrix) for the depicted dimension of the
                                                Dirichlet DOF.
            realized_random_field_2 (np.array): Array containing values of the random field (each
                                                row is associated to a corresponding row in the
                                                coordinate matrix) for the depicted dimension of the
                                                Dirichlet DOF.
            realized_random_field_3 (np.array): Array containing values of the random field (each
                                                row is associated to a corresponding row in the
                                                coordinate matrix) for the depicted dimension of the
                                                Dirichlet DOF.
            fun_1 (np.array): Array containing integer identifiers for functions that are applied to
                              associated dimension of the random field. This is a BACI specific
                              function that might, e.g., vary in time.
            fun_2 (np.array): Array containing integer identifiers for functions that are applied to
                              associated dimension of the random field. This is a BACI specific
                              function that might, e.g., vary in time.
            fun_3 (np.array): Array containing integer identifiers for functions that are applied to
                              associated dimension of the random field. This is a BACI specific
                              function that might, e.g., vary in time.

        """
        # take care of random dirichlet fields
        realized_random_field_1 = realized_random_field_2 = realized_random_field_3 = None
        fun_1 = fun_2 = fun_3 = None
        for dirich_field in fields_dirich_on_geo_set:
            set_shape = dirich_field['values'].shape
            if dirich_field["external_definition"]["dof_for_field"] == 1:
                realized_random_field_1 = dirich_field['values']
                fun_1 = dirich_field["external_definition"]["funct_for_field"] * np.ones(set_shape)

            elif dirich_field["external_definition"]["dof_for_field"] == 2:
                realized_random_field_2 = dirich_field["values"]
                fun_2 = dirich_field["external_definition"]["funct_for_field"] * np.ones(set_shape)

            elif dirich_field["external_definition"]["dof_for_field"] == 3:
                realized_random_field_3 = dirich_field["values"]
                fun_3 = dirich_field["external_definition"]["funct_for_field"] * np.ones(set_shape)

        return (
            realized_random_field_1,
            realized_random_field_2,
            realized_random_field_3,
            fun_1,
            fun_2,
            fun_3,
        )

    @staticmethod
    def _assign_deterministic_dirichlet_fields_per_geo_set(
        fields_dirich_on_geo_set,
        realized_random_field_1,
        realized_random_field_2,
        realized_random_field_3,
        fun_1,
        fun_2,
        fun_3,
    ):
        """
        Adopt and write the constant or determinsitic DOFs of the Dirichlet point conditions.
        These conditions did not exist before but only one DOF at each discrete point might be
        drawn form a random field; the other DOFs might be a constant value, e.g., 0.

        Args:
            fields_dirich_on_geo_set (lst): List containing the descriptions and a
                                            realization of the Dirichlet BCs random fields.
            realized_random_field_1 (np.array): Array containing values of the random field (each
                                                row is associated to a corresponding row in the
                                                coordinate matrix) for the depicted dimension of the
                                                Dirichlet DOF.
            realized_random_field_2 (np.array): Array containing values of the random field (each
                                                row is associated to a corresponding row in the
                                                coordinate matrix) for the depicted dimension of the
                                                Dirichlet DOF.
            realized_random_field_3 (np.array): Array containing values of the random field (each
                                                row is associated to a corresponding row in the
                                                coordinate matrix) for the depicted dimension of the
                                                Dirichlet DOF.
            fun_1 (np.array): Array containing integer identifiers for functions that are applied to
                              associated dimension of the random field. This is a BACI specific
                              function that might, e.g., vary in time.
            fun_2 (np.array): Array containing integer identifiers for functions that are applied to
                              associated dimension of the random field. This is a BACI specific
                              function that might, e.g., vary in time.
            fun_3 (np.array): Array containing integer identifiers for functions that are applied to
                              associated dimension of the random field. This is a BACI specific
                              function that might, e.g., vary in time.

        Returns:
            realized_random_field_1 (np.array): Array containing values of the random field (each
                                                row is associated to a corresponding row in the
                                                coordinate matrix) for the depicted dimension of the
                                                Dirichlet DOF.
            realized_random_field_2 (np.array): Array containing values of the random field (each
                                                row is associated to a corresponding row in the
                                                coordinate matrix) for the depicted dimension of the
                                                Dirichlet DOF.
            realized_random_field_3 (np.array): Array containing values of the random field (each
                                                row is associated to a corresponding row in the
                                                coordinate matrix) for the depicted dimension of the
                                                Dirichlet DOF.
            fun_1 (np.array): Array containing integer identifiers for functions that are applied to
                              associated dimension of the random field. This is a BACI specific
                              function that might, e.g., vary in time.
            fun_2 (np.array): Array containing integer identifiers for functions that are applied to
                              associated dimension of the random field. This is a BACI specific
                              function that might, e.g., vary in time.
            fun_3 (np.array): Array containing integer identifiers for functions that are applied to
                              associated dimension of the random field. This is a BACI specific
                              function that might, e.g., vary in time.

        """
        # TODO see how this behaves for several fields
        set_shape = fields_dirich_on_geo_set[0]['values'].shape
        for deter_dof, value_deter_dof, funct_deter in zip(
            fields_dirich_on_geo_set[0]['external_definition']["dofs_deterministic"],
            fields_dirich_on_geo_set[0]['external_definition']["value_dofs_deterministic"],
            fields_dirich_on_geo_set[0]['external_definition']["funct_for_deterministic_dofs"],
        ):
            if deter_dof == 1:
                if realized_random_field_1 is None:
                    realized_random_field_1 = value_deter_dof * np.ones(set_shape)
                    fun_1 = funct_deter * np.ones(set_shape)
                else:
                    raise ValueError(
                        "Dof 1 of geometric set is already defined and cannot be set to a "
                        "deterministic value now. Abort..."
                    )
            elif deter_dof == 2:
                if realized_random_field_2 is None:
                    realized_random_field_2 = value_deter_dof * np.ones(set_shape)
                    fun_2 = funct_deter * np.ones(set_shape)
                else:
                    raise ValueError(
                        "Dof 2 of geometric set is already defined and cannot be set to a "
                        "deterministic value now. Abort..."
                    )
            elif deter_dof == 3:
                if realized_random_field_2 is None:
                    realized_random_field_2 = value_deter_dof * np.ones(set_shape)
                    fun_2 = funct_deter * np.ones(set_shape)
                else:
                    raise ValueError(
                        "Dof 3 of geometric set is already defined and cannot be set to a "
                        "deterministic value now. Abort..."
                    )

        # catch fields that were not set
        if fun_1 is None or fun_2 is None or fun_3 is None:
            raise ValueError("One BACI function of a Dirichlet DOF was not defined! Abort...")
        if (
            realized_random_field_1 is None
            or realized_random_field_2 is None
            or realized_random_field_3 is None
        ):
            raise ValueError(
                "One random fields realization for a Dirichlet BC was not " "defined. Abort..."
            )

        return (
            realized_random_field_1,
            realized_random_field_2,
            realized_random_field_3,
            fun_1,
            fun_2,
            fun_3,
        )

    def _get_my_topology(self, geo_set_name_type):
        # TODO this is problematic as topology has not been read it for the new object
        if geo_set_name_type == 'DNODE':
            my_topology = self.node_topology

        elif geo_set_name_type == 'DLINE':
            my_topology = self.line_topology

        elif geo_set_name_type == 'DSURFACE':
            my_topology = self.surface_topology

        elif geo_set_name_type == 'DVOL':
            my_topology = self.volume_topology
        else:
            my_topology = None
        return my_topology

    def _create_new_node_sets(self, random_fields_lst):
        """
        From a given geometric set of interest: Identify associated nodes and add them as a new
        node-set to the geometric set-description of the external external_geometry_obj.

        Args:
            random_fields_lst (lst): List containing descriptions of involved random fields

        Returns:
            None

        """
        # iterate through all random fields that encode BCs
        BCs_random_fields = (
            random_field
            for random_field in random_fields_lst
            if (
                (random_field["external_definition"]["type"] == "dirichlet")
                or (random_field["external_definition"]["type"] == "neumann")
                or (random_field["external_definition"]["type"] == "transport_dirichlet")
            )
        )
        nodes_mesh_lst = []  # note, this is a list of dicts
        for random_field in BCs_random_fields:
            # get associated geometric set
            topology_name = random_field["external_definition"]["external_instance"]
            topology_type = topology_name.split()[0]
            # check if line, surf or vol
            my_topology_lst = self._get_my_topology(topology_type)
            nodes_mesh_lst.extend(
                [
                    {"node_mesh": topo['node_mesh'], "topo_dnodes": [], "name": topology_name}
                    for topo in my_topology_lst
                    if topo['topology_name'] == topology_name
                ]
            )

        # create the corresponding point geometric set and save the mapping in a list/dict per rf
        # check the highest dnode and start after that one
        if int(self.design_description['NDPOINT']) > 0:
            ndnode_min = int(self.design_description['NDPOINT']) + 1
        else:
            ndnode_min = 1

        for num, _ in enumerate(nodes_mesh_lst):
            if num == 0:
                nodes_mesh_lst[num]["topo_dnodes"] = np.arange(
                    ndnode_min, ndnode_min + len(nodes_mesh_lst[num]["node_mesh"])
                )
            else:
                last_node = nodes_mesh_lst[num - 1]["topo_dnodes"][-1]
                nodes_mesh_lst[num]["topo_dnodes"] = np.arange(
                    last_node, last_node + len(nodes_mesh_lst[num]["node_mesh"])
                )

        self.new_nodes_lst = nodes_mesh_lst

    def _write_new_node_sets(self):
        """
        Write the new node sets to the dat-file as individual dnodes.

        Returns:
            None

        """
        for node_set in self.new_nodes_lst:
            for mesh_node, topo_node in zip(node_set['node_mesh'], node_set['topo_dnodes']):
                print(f"NODE {mesh_node} DNODE {topo_node}")