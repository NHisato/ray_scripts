""" Add objectives

    Contains functions required to load objectives from xml files
    add the objectives to RayStation. Contains functions for reassignment of an
    objective when the target name is not matched
"""
import sys
import os
import logging
import datetime
import xml.etree.ElementTree
import connect
import Objectives
import UserInterface


def select_objective_protocol():
    """

    :return: tree: Elementtree with user-selected objectives loaded
    """
    protocol_folder = r'../protocols'
    objective_folder = r'objectives'
    institution_folder = r'UW'
    path_objectives = os.path.join(os.path.dirname(__file__),
                                   protocol_folder,
                                   institution_folder,
                                   objective_folder)
    tpo = UserInterface.TpoDialog()
    tpo.load_protocols(path_objectives)
    input_dialog = UserInterface.InputDialog(
        inputs={'i': 'Select Objective Set'},
        title='Objective Selection',
        datatype={'i': 'combo'},
        initial={},
        options={'i': list(tpo.protocols.keys())},
        required=['i'])
    response = input_dialog.show()
    # Close on cancel
    if response == {}:
        logging.info('create_objective cancelled by user')
        status.finish('User cancelled create objective creation.')
        sys.exit('create_objective cancelled by user')
    logging.debug('user selected {}').format(input_dialog.values['i'])
    tree = Objectives.select_objectives(input_dialog.values['i'])
    return tree


def main():
    """ Temp chunk of code to try to open an xml file"""
    try:
        patient = connect.get_current('Patient')
        case = connect.get_current("Case")
        examination = connect.get_current("Examination")
        plan = connect.get_current("Plan")
        beamset = connect.get_current("BeamSet")
    except:
        logging.warning("patient, case and examination must be loaded")

    protocol_folder = r'../protocols'
    institution_folder = r'UW'
    file = 'planning_structs_conventional.xml'
    path_protocols = os.path.join(os.path.dirname(__file__), protocol_folder, institution_folder, file)
    tree = Objectives.select_objectives(filename=path_protocols)
    tree = select_objective_protocol()
    logging.debug("selected file {}".format(path_protocols))
    # TODO::
    # Extend this for multiple objective sets found within a file
    # Consider adding functionality for protocols, orders, etc...
    # Parse each type in a separate function
    # Add matching elements
    # Add objective function should know whether something is absolute or relative for dose and volume
    if tree.getroot().tag == 'objectiveset':
        logging.debug("parsing xml: {}".format(file))
        n = tree.find('name').text
        logging.debug('Found protocol {} in {}'.format(n, file))
        objectiveset = tree.getroot()
        objectives = objectiveset.findall('./objectives/roi')
        for o in objectives:
            o_name = o.find('name').text
            o_type = o.find('type').text
            # TESTING ONLY - TO DO ELIMINATE THIS NEXT LINE
            # This will need to be a user supplied dose level.
            if o.find('dose').attrib['units'] == '%':
                s_dose = '50'
            else:
                s_dose = None

            Objectives.add_objective(o,
                                     case=case,
                                     plan=plan,
                                     beamset=beamset,
                                     s_roi=None,
                                     s_dose=s_dose,
                                     s_weight=None,
                                     restrict_beamset=None)
    else:
        logging.debug('Could not find objective set using tree = {}'.format(tree))


if __name__ == '__main__':
    main()
