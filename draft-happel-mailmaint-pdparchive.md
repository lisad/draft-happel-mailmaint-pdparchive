---
title: "Personal Data Portability Archive"
abbrev: "PDPArchive"
category: std

docname: draft-happel-mailmaint-pdparchive-latest
submissiontype: IETF
number:
date:
consensus: true
v: 2
area: "Applications and Real-Time"
workgroup: mailmaint
keyword:
 - email
 - calendaring
 - archive
 - personal
 - portability
venue:
  group: mailmaint
  type: "Working Group"
  mail: "mailmaint@ietf.org"
  arch: "https://mailarchive.ietf.org/arch/browse/mailmaint/"
  github: "lisad/draft-happel-mailmaint-pdparchive"
  latest: "https://lisad.github.io/draft-happel-mailmaint-pdparchive/draft-happel-mailmaint-pdparchive.html"

author:
 -
    ins: L. Dusseault
    fullname: Lisa Dusseault
    organization: Data Transfer Initiative
    email: lisa@dtinit.org
 -
    ins: H.J. Happel
    fullname: Hans-Joerg Happel
    organization: audriga
    email: hans-joerg@audriga.com

 -
    ins: A. Melnikov
    fullname: Alexey Melnikov
    organization: "Isode Ltd"
    email: Alexey.Melnikov@isode.com

normative:

  RFC5322:

  RFC8984:

  RFC9553:

informative:

  RFC822:

  RFC2822:

  RFC4155:

  RFC5545:

  RFC5598:

  RFC6350:

  PST:
    title: "[MS-PST]: Outlook Personal Folders (.pst) File Format"
    target: https://learn.microsoft.com/en-us/openspecs/office_file_formats/ms-pst/141923d5-15ab-4ef1-a524-6dce75aae546
    author:
     - org: Microsoft
    date: false

  GoogleTakeout:
    title: Google Takeout
    target: https://takeout.google.com/settings/takeout
    author:
     - org: Google
    date: false


...

--- abstract

This document proposes the Personal Data Portability Archive format (PDPA), suitable for import/export, backup/restore, and data transfer scenarios for personal data.


--- middle

# Introduction

As part of communication protocols, the IETF has standardized a number of data formats such as the Internet Message Format {{RFC5322}}, vCard {{RFC6350}}, iCalendar {{RFC5545}}, or, more recently, JSContact {{RFC9553}} and JSCalendar {{RFC8984}}.

While mainly designed for interoperability, many of these data formats have also become popular for data portability, i.e., the import/export of data across different services. The growing importance of data portability however demands for an open standard archive format which can deal with different types of personal data in a homogeneous fashion.

To this end, this document proposes the Personal Data Portability Archive format (PDPA), suitable for import/export, backup/restore, and data transfer scenarios for personal data. It is compatible with both IMAP and JMAP and should be suitable as an interchange format between related software and services such as for email, contacts, calendaring, tasks, or files.

The approach is to define JSON formats (using CDDL), folder structure, and a common compression format.  Additional specifications will likely define a protocol how these files can be requested from, imported into, or transferred between servers.

# Conventions and Definitions

The term "personal data" refers to persistent data which users created and managed within applications or services. Classic examples are emails, contacts, calendars, tasks, notes, or files. Other examples might be fitness tracking records, energy bills, or location history.

The term "data portability" refers to the right or technical procedure to use or transfer personal data across different applications or services.

The terms "message" and "email message" refer to "electronic mail messages" or "emails" as specified in {{RFC5322}}. The term "Message User Agent" (MUA) denotes an email client application as per {{RFC5598}}.

{::boilerplate bcp14-tagged}

# Goals

The core goal is to provide an open and extensible archive and transfer format for personal data. This includes data types that are subject of existing IETF protocols, such as email and groupware data (e.g., contacts, calendars, tasks) but may also include further types of personal data.

Goals will be refined by use cases and cross-cutting technical goals in the following sub-sections.

JSON is used as a widely interoperable base format that systems can easily translate their internal data representation into. Wherever possible, fields, values and data structures are derived from existing IMAP/JMAP specifications to remain compatible with both.

## Use cases

### Data portability

A main use case for the novel format is to allow exporting the full user data managed by services or software products into a simple file (or set of files) which is under full control of the user.

The user might use such export for backup, archiving, or for importing when switching to another service or software (i.e., migration).

Depending on the type of data, exporting/importing can be a time-consuming process. Particularly for the case of switching services, PDPA should allow to minimize the time period during which a user cannot use the origin system but also the destination system is not yet ready.

### Incremental backup

Beyond snapshot backups/exports, the format should optionally allow for incremental backups.

There are at least two scenarios for this:

* Software which wants to keep a permanent, incremental mirror of user data (e.g., for instant export or restore)
* Users regularly exporting changes in data managed by services or software products

### Synchronization

Data portability does not just allow users to switch from one service to another one, but to let users benefit from 3rd party services getting a copy of their data  (at the request of the user).  Simple synchronization features could make this much better.

For example, current online systems that allow importing contacts are not often suited to maintaining one's address book on two systems. Re-importing a contact into a system that already has that contact often results in duplicating the exact same contact, whether or not there have been edits, making repeated synchronization practically infeasible. It should be easy to do a significantly better job of this with some attention to object IDs and modification timestamps.

We however do not attempt to solve two-way synchronization via export files.  It would require significant additional work to allow two systems, neither of which is agreed-upon to be the source of truth, to reliably synchronize changes from both. In comparison, solving one-way synchronization only requires agreed-upon usage of existing fields and values.

### Dataset exchange

PDPA should be usable to exchange and share larger data sets than just one user, or to share a single user's data outside the context where the user knows what it is and where it came from.

Potential applications of this are:

* The ability to exchange test data and known mailstore state, e.g. for conformance testing or internal functional tests
* Legal discovery and forensics use cases may benefit from a standard export format, such that investigators can expect a great deal of consistency when collecting data from different systems.
* Researchers may be able to collect archive files through data donations and use as input to research.

While these use cases may suggest small features that would help these use cases be successful, supporting more advanced features required by these use cases is not a priority. For example, we do not attempt to cryptographically solve provenance for use in legal and forensics use cases.

### Data persistence

The format MAY be used as a development-time active persistence layer for user data in, e.g., email clients or applications. It is not intended as, or suitable for, a production-level persistence layer.

## Technical Goals

Besides actual use cases, there are a number of side requirements and goals for PDPA.

### Email standards compatibility

Data formats should aim for compatibility with JMAP data formats for the sake of interoperability and synergies in software libraries.

Dedicated JMAP API methods for exporting and importing the format described here, or for related server-to-server transfer protocols are out of the scope of this document.

Due to its specifics and ubiquitous usage, the Internet Message Format {{RFC5322}}; latest revision of {{RFC2822}}/{{RFC822}} should be the core of representing individual email data.

This specification should ideally describe mappings between PDPA and existing mailbox persistence schemes such as Maildir or MBOX {{RFC4155}}.

### Interoperability

It should be mostly possible to use personal data exports from one system with different software or services.  When a source exports personal data it can include all the information it would need for a fully-functional import, _however_ destination systems running different software may not be able to import all of that information (especially if it includes non-standard features) and use it exactly the same way.  This specification does not attempt to achieve perfect interoperability between diverse systems, but instead to make reasonable trade-offs.

### Extensibility

This format should be extensible to accommodate types of personal data not explicitly mentioned or foreseen when writing these specs.

### Flexible granularity

This format should allow flexible granularity in two ways:

1) It should enable easy access to separate types of data (e.g., emails vs. contacts), e.g. to allow for partial imports or exports

2) While ideally representable as a single file, archives may also span several files due to reasons such as file size restrictions or incremental generation logic.

(The ability for a user to export and/or backup an entire email account requires some accommodation of large amounts of data and risks of interruptions in downloads.  Splitting exports into multiple files during export is one possible solution.)

### Accessible for local tooling

PDPA should allow easy access for local tools (e.g., CLIs). While this may sound obvious, it is a key factor for the intended versatility of the format.

### Efficiency

Since certain kinds of personal data might involve large quantities of data, major use cases for PDPA should be realizable in an efficient manner.

For now, this is stated as an abstract guiding principle. Its actual dimensions and trade-offs need to be refined while evolving this specification.

## Related work

Many email server implementors have found it desirable to have one or more file formats for storing email in a file system even when the primary active email storage is more commonly a database.  Examples include {{PST}} files (Outlook), NSF (Notes), {{GoogleTakeout}}, Maildir, MBOX.  File formats are already used for interoperability in many cases even when not standardized.

This specification follows that pattern in order to build on these partial successes.  By standardizing one format, we expect to be able to satisfy use cases that are harder to satisfy with a plurality of formats, such as use cases for server-to-server transfer of email account data during account migrations.  Specifications that explain how to create these archives in different situations can refer to this specification.

# Security Considerations

TODO Security


# IANA Considerations

This document has no IANA actions.


--- back

# Acknowledgments
{:numbered="false"}

TODO acknowledge.
