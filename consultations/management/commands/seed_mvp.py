from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Product, ProductCategory
from consultations.models import AIResponseReview, ConsultationMessage, ConsultationSession, UnansweredQuestion
from knowledge.models import KnowledgeCategory, KnowledgeEntry


class Command(BaseCommand):
    help = "Seed data awal untuk MVP konsultasi herbal"

    @transaction.atomic
    def handle(self, *args, **options):
        user_model = get_user_model()

        admin_user, _ = user_model.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@naturalva.local",
                "first_name": "System",
                "last_name": "Admin",
                "role": user_model.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin_user.role = user_model.Role.ADMIN
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.set_password("Admin12345!")
        admin_user.save()

        trainer_user, _ = user_model.objects.get_or_create(
            username="trainer",
            defaults={
                "email": "trainer@naturalva.local",
                "first_name": "AI",
                "last_name": "Trainer",
                "role": user_model.Role.AI_TRAINER,
            },
        )
        trainer_user.role = user_model.Role.AI_TRAINER
        trainer_user.set_password("Trainer12345!")
        trainer_user.save()

        customer_user, _ = user_model.objects.get_or_create(
            username="customer",
            defaults={
                "email": "customer@naturalva.local",
                "first_name": "Demo",
                "last_name": "Customer",
                "role": user_model.Role.CUSTOMER,
            },
        )
        customer_user.role = user_model.Role.CUSTOMER
        customer_user.set_password("Customer12345!")
        customer_user.save()

        digest_category, _ = ProductCategory.objects.get_or_create(
            name="Pencernaan",
            defaults={"description": "Produk herbal untuk membantu kenyamanan sistem pencernaan."},
        )
        immunity_category, _ = ProductCategory.objects.get_or_create(
            name="Daya Tahan Tubuh",
            defaults={"description": "Produk herbal untuk membantu menjaga imunitas dan kebugaran."},
        )
        respiratory_category, _ = ProductCategory.objects.get_or_create(
            name="Pernapasan",
            defaults={"description": "Produk herbal untuk membantu menjaga kenyamanan saluran pernapasan."},
        )
        women_category, _ = ProductCategory.objects.get_or_create(
            name="Kewanitaan",
            defaults={"description": "Produk herbal untuk membantu menjaga kenyamanan tubuh wanita."},
        )
        vitality_category, _ = ProductCategory.objects.get_or_create(
            name="Stamina",
            defaults={"description": "Produk herbal untuk membantu menjaga energi dan kebugaran harian."},
        )

        products = [
            {
                "category": digest_category,
                "name": "Herba Lambung Sehat",
                "slug": "herba-lambung-sehat",
                "description": "Produk herbal untuk membantu meredakan rasa tidak nyaman pada lambung dan pencernaan.",
                "benefits": "Membantu mengurangi rasa perih, mual ringan, dan ketidaknyamanan setelah makan.",
                "usage_instructions": "Dikonsumsi 2 kali sehari setelah makan sesuai anjuran kemasan.",
                "contraindications": "Hindari penggunaan tanpa konsultasi lebih lanjut pada ibu hamil, menyusui, atau pengguna obat rutin tertentu.",
            },
            {
                "category": digest_category,
                "name": "Herba Pencernaan Nyaman",
                "slug": "herba-pencernaan-nyaman",
                "description": "Produk herbal untuk membantu menjaga kenyamanan perut saat kembung atau begah.",
                "benefits": "Membantu mengurangi rasa penuh, kembung ringan, dan ketidaknyamanan setelah pola makan tidak teratur.",
                "usage_instructions": "Dikonsumsi 2 kali sehari setelah makan sesuai anjuran kemasan.",
                "contraindications": "Perlu kehati-hatian pada pengguna dengan keluhan pencernaan berat atau berkepanjangan.",
            },
            {
                "category": immunity_category,
                "name": "Herba Imuno Plus",
                "slug": "herba-imuno-plus",
                "description": "Produk herbal untuk membantu menjaga daya tahan tubuh sehari-hari.",
                "benefits": "Membantu menjaga kebugaran, stamina, dan daya tahan tubuh.",
                "usage_instructions": "Dikonsumsi 1 sampai 2 kali sehari sesuai kebutuhan dan anjuran kemasan.",
                "contraindications": "Perhatikan reaksi tubuh bila memiliki riwayat alergi terhadap bahan herbal tertentu.",
            },
            {
                "category": immunity_category,
                "name": "Herba Fit Sehari",
                "slug": "herba-fit-sehari",
                "description": "Produk herbal untuk membantu menjaga kondisi tubuh tetap prima saat aktivitas padat.",
                "benefits": "Membantu menjaga kebugaran harian dan mendukung tubuh tetap segar.",
                "usage_instructions": "Dikonsumsi 1 kali sehari pada pagi atau siang hari sesuai anjuran kemasan.",
                "contraindications": "Hentikan penggunaan bila muncul reaksi yang tidak nyaman dan konsultasikan lebih lanjut bila diperlukan.",
            },
            {
                "category": respiratory_category,
                "name": "Herba Lega Nafas",
                "slug": "herba-lega-nafas",
                "description": "Produk herbal untuk membantu menjaga kenyamanan tenggorokan dan pernapasan.",
                "benefits": "Membantu meredakan rasa tidak nyaman di tenggorokan dan membantu tubuh terasa lebih lega.",
                "usage_instructions": "Dikonsumsi sesuai anjuran kemasan, terutama saat tubuh memerlukan dukungan kenyamanan pernapasan.",
                "contraindications": "Perlu konsultasi lebih dulu bagi pengguna dengan riwayat gangguan pernapasan yang sering kambuh.",
            },
            {
                "category": women_category,
                "name": "Herba Nyaman Wanita",
                "slug": "herba-nyaman-wanita",
                "description": "Produk herbal untuk membantu menjaga kenyamanan tubuh wanita saat masa tertentu.",
                "benefits": "Membantu menjaga kenyamanan tubuh, mendukung relaksasi, dan membantu aktivitas tetap berjalan dengan baik.",
                "usage_instructions": "Dikonsumsi sesuai anjuran kemasan pada masa tubuh membutuhkan dukungan kenyamanan tambahan.",
                "contraindications": "Tidak disarankan digunakan tanpa arahan lebih lanjut pada ibu hamil atau kondisi hormonal tertentu.",
            },
            {
                "category": vitality_category,
                "name": "Herba Stamina Prima",
                "slug": "herba-stamina-prima",
                "description": "Produk herbal untuk membantu menjaga stamina dan energi harian.",
                "benefits": "Membantu mendukung daya tahan aktivitas, menjaga kebugaran, dan mengurangi rasa lelah ringan.",
                "usage_instructions": "Dikonsumsi 1 kali sehari setelah makan sesuai anjuran kemasan.",
                "contraindications": "Perlu kehati-hatian bagi pengguna dengan kondisi kesehatan khusus atau yang sedang mengonsumsi obat rutin.",
            },
        ]

        for payload in products:
            Product.objects.update_or_create(
                slug=payload["slug"],
                defaults={**payload, "is_active": True},
            )
        seeded_products = {
            product.name: product
            for product in Product.objects.filter(slug__in=[payload["slug"] for payload in products])
        }

        kb_faq, _ = KnowledgeCategory.objects.get_or_create(
            name="FAQ",
            defaults={"description": "Pertanyaan umum pelanggan terkait produk dan konsultasi herbal."},
        )
        kb_usage, _ = KnowledgeCategory.objects.get_or_create(
            name="Aturan Pakai",
            defaults={"description": "Panduan penggunaan produk herbal."},
        )
        kb_contra, _ = KnowledgeCategory.objects.get_or_create(
            name="Kontraindikasi",
            defaults={"description": "Informasi kehati-hatian dan kondisi yang perlu diperhatikan."},
        )
        kb_product_benefit, _ = KnowledgeCategory.objects.get_or_create(
            name="Manfaat Produk",
            defaults={"description": "Ringkasan manfaat utama tiap produk herbal."},
        )
        kb_consultation, _ = KnowledgeCategory.objects.get_or_create(
            name="Panduan Konsultasi",
            defaults={"description": "Aturan layanan konsultasi herbal berbasis AI."},
        )

        entries = [
            {
                "category": kb_faq,
                "title": "Kapan produk herbal sebaiknya dikonsumsi",
                "question": "Kapan waktu terbaik mengonsumsi produk herbal?",
                "answer": "Waktu konsumsi mengikuti aturan pakai pada masing-masing produk. Secara umum, produk herbal dikonsumsi sesuai anjuran kemasan dan perlu memperhatikan kondisi tubuh pengguna.",
                "source_type": KnowledgeEntry.SourceType.FAQ,
                "keywords": "waktu konsumsi, aturan pakai, penggunaan produk",
            },
            {
                "category": kb_usage,
                "title": "Aturan pakai Herba Lambung Sehat",
                "question": "Bagaimana aturan pakai Herba Lambung Sehat?",
                "answer": "Herba Lambung Sehat dikonsumsi 2 kali sehari setelah makan sesuai anjuran kemasan dan disesuaikan dengan kondisi pengguna.",
                "source_type": KnowledgeEntry.SourceType.PRODUCT,
                "keywords": "herba lambung sehat, lambung, aturan pakai",
            },
            {
                "category": kb_usage,
                "title": "Aturan pakai Herba Imuno Plus",
                "question": "Bagaimana aturan pakai Herba Imuno Plus?",
                "answer": "Herba Imuno Plus dapat dikonsumsi 1 sampai 2 kali sehari sesuai kebutuhan dan anjuran kemasan.",
                "source_type": KnowledgeEntry.SourceType.PRODUCT,
                "keywords": "herba imuno plus, imunitas, daya tahan tubuh",
            },
            {
                "category": kb_usage,
                "title": "Aturan pakai Herba Lega Nafas",
                "question": "Bagaimana aturan pakai Herba Lega Nafas?",
                "answer": "Herba Lega Nafas dikonsumsi sesuai anjuran kemasan, terutama saat tubuh memerlukan dukungan kenyamanan pada tenggorokan dan pernapasan.",
                "source_type": KnowledgeEntry.SourceType.PRODUCT,
                "keywords": "herba lega nafas, tenggorokan, pernapasan, aturan pakai",
            },
            {
                "category": kb_usage,
                "title": "Aturan pakai Herba Stamina Prima",
                "question": "Bagaimana aturan pakai Herba Stamina Prima?",
                "answer": "Herba Stamina Prima dikonsumsi 1 kali sehari setelah makan sesuai anjuran kemasan untuk membantu menjaga kebugaran saat aktivitas padat.",
                "source_type": KnowledgeEntry.SourceType.PRODUCT,
                "keywords": "herba stamina prima, stamina, energi, aturan pakai",
            },
            {
                "category": kb_product_benefit,
                "title": "Manfaat Herba Lambung Sehat",
                "question": "Apa manfaat Herba Lambung Sehat?",
                "answer": "Herba Lambung Sehat membantu mengurangi rasa tidak nyaman pada lambung, mual ringan, dan sensasi perih setelah makan.",
                "source_type": KnowledgeEntry.SourceType.PRODUCT,
                "keywords": "manfaat herba lambung sehat, lambung, mual, perih",
            },
            {
                "category": kb_product_benefit,
                "title": "Manfaat Herba Pencernaan Nyaman",
                "question": "Apa manfaat Herba Pencernaan Nyaman?",
                "answer": "Herba Pencernaan Nyaman membantu menjaga kenyamanan perut saat terasa kembung, penuh, atau begah setelah pola makan tidak teratur.",
                "source_type": KnowledgeEntry.SourceType.PRODUCT,
                "keywords": "manfaat herba pencernaan nyaman, kembung, begah, pencernaan",
            },
            {
                "category": kb_product_benefit,
                "title": "Manfaat Herba Imuno Plus",
                "question": "Apa manfaat Herba Imuno Plus?",
                "answer": "Herba Imuno Plus membantu menjaga daya tahan tubuh, kebugaran, dan stamina harian.",
                "source_type": KnowledgeEntry.SourceType.PRODUCT,
                "keywords": "manfaat herba imuno plus, imun, stamina, daya tahan tubuh",
            },
            {
                "category": kb_product_benefit,
                "title": "Manfaat Herba Lega Nafas",
                "question": "Apa manfaat Herba Lega Nafas?",
                "answer": "Herba Lega Nafas membantu menjaga kenyamanan tenggorokan dan mendukung tubuh terasa lebih lega saat ada ketidaknyamanan ringan pada pernapasan.",
                "source_type": KnowledgeEntry.SourceType.PRODUCT,
                "keywords": "manfaat herba lega nafas, tenggorokan, napas, pernapasan",
            },
            {
                "category": kb_contra,
                "title": "Kehati-hatian penggunaan produk herbal",
                "question": "Siapa yang perlu berhati-hati saat menggunakan produk herbal?",
                "answer": "Pengguna dengan kondisi khusus seperti ibu hamil, ibu menyusui, penderita penyakit tertentu, atau pengguna obat rutin perlu berhati-hati dan sebaiknya melakukan konsultasi lebih lanjut sebelum menggunakan produk herbal.",
                "source_type": KnowledgeEntry.SourceType.FAQ,
                "keywords": "kontraindikasi, kehati-hatian, ibu hamil, obat rutin",
            },
            {
                "category": kb_contra,
                "title": "Kapan konsultasi medis diperlukan",
                "question": "Kapan pengguna harus mencari bantuan tenaga kesehatan?",
                "answer": "Jika keluhan terasa berat, memburuk, berulang, atau disertai gejala lain yang mengganggu aktivitas, pengguna perlu berkonsultasi dengan tenaga kesehatan dan tidak hanya mengandalkan informasi herbal.",
                "source_type": KnowledgeEntry.SourceType.SOP,
                "keywords": "konsultasi medis, keluhan berat, gejala berulang, tenaga kesehatan",
            },
            {
                "category": kb_faq,
                "title": "Batas sistem konsultasi herbal",
                "question": "Apakah sistem ini memberikan diagnosis medis?",
                "answer": "Sistem ini memberikan informasi awal terkait produk herbal dan bukan pengganti diagnosis medis. Jika keluhan berat atau berlanjut, pengguna perlu berkonsultasi dengan tenaga kesehatan.",
                "source_type": KnowledgeEntry.SourceType.SOP,
                "keywords": "diagnosis, medis, konsultasi awal, batas sistem",
            },
            {
                "category": kb_faq,
                "title": "Apakah produk herbal bisa diminum bersamaan dengan obat rutin",
                "question": "Bolehkah produk herbal digunakan bersama obat rutin?",
                "answer": "Penggunaan bersamaan dengan obat rutin memerlukan kehati-hatian. Pengguna sebaiknya berkonsultasi lebih dahulu untuk menilai kecocokan dan mengurangi risiko interaksi yang tidak diinginkan.",
                "source_type": KnowledgeEntry.SourceType.FAQ,
                "keywords": "obat rutin, interaksi, kontraindikasi, konsultasi",
            },
            {
                "category": kb_faq,
                "title": "Apakah semua keluhan cocok dengan produk herbal",
                "question": "Apakah semua keluhan bisa ditangani dengan produk herbal?",
                "answer": "Tidak semua keluhan cocok ditangani hanya dengan produk herbal. Sistem hanya membantu memberi informasi awal berbasis knowledge base dan tidak menggantikan pemeriksaan medis.",
                "source_type": KnowledgeEntry.SourceType.FAQ,
                "keywords": "semua keluhan, diagnosis, batas sistem, pemeriksaan medis",
            },
            {
                "category": kb_consultation,
                "title": "Cara kerja konsultasi herbal berbasis AI",
                "question": "Bagaimana sistem konsultasi ini menjawab pertanyaan pengguna?",
                "answer": "Sistem akan mencari konteks dari knowledge base dan data produk yang relevan, lalu menyusun jawaban AI berdasarkan konteks tersebut. Jika konteks tidak cukup, pertanyaan akan disimpan sebagai unanswered question untuk ditinjau AI Trainer.",
                "source_type": KnowledgeEntry.SourceType.SOP,
                "keywords": "rag, knowledge base, unanswered question, ai trainer",
            },
            {
                "category": kb_consultation,
                "title": "Panduan menulis pertanyaan konsultasi",
                "question": "Bagaimana cara menulis pertanyaan agar jawaban lebih relevan?",
                "answer": "Pengguna dianjurkan menuliskan keluhan atau kebutuhan secara singkat dan jelas, misalnya menyebut kondisi yang dirasakan, tujuan penggunaan, serta produk yang ingin ditanyakan bila ada.",
                "source_type": KnowledgeEntry.SourceType.SOP,
                "keywords": "cara bertanya, prompt, konsultasi, pertanyaan relevan",
            },
        ]

        seeded_entries = {}
        for payload in entries:
            entry, _ = KnowledgeEntry.objects.update_or_create(
                title=payload["title"],
                defaults={
                    **payload,
                    "status": KnowledgeEntry.Status.PUBLISHED,
                    "created_by": trainer_user,
                },
            )
            seeded_entries[payload["title"]] = entry

        ConsultationSession.objects.filter(user=customer_user).delete()

        session_one = ConsultationSession.objects.create(
            user=customer_user,
            title="Produk untuk lambung sensitif",
            status=ConsultationSession.Status.CLOSED,
        )
        ConsultationMessage.objects.create(
            session=session_one,
            product=seeded_products["Herba Lambung Sehat"],
            sender=ConsultationMessage.Sender.USER,
            content="Saya sering merasa perut perih setelah telat makan, produk herbal apa yang cocok?",
        )
        ai_message_one = ConsultationMessage.objects.create(
            session=session_one,
            product=seeded_products["Herba Lambung Sehat"],
            sender=ConsultationMessage.Sender.AI,
            content="Berdasarkan knowledge base, Herba Lambung Sehat dapat dipertimbangkan untuk membantu mengurangi rasa tidak nyaman pada lambung dan mual ringan setelah makan. Produk ini umumnya dikonsumsi 2 kali sehari setelah makan sesuai anjuran kemasan. Jika keluhan terasa berat atau sering berulang, sebaiknya lakukan konsultasi lebih lanjut dengan tenaga kesehatan.",
            confidence_score=0.89,
            used_rag=True,
            response_state=ConsultationMessage.ResponseState.ANSWERED,
            source_summary="KB: Manfaat Herba Lambung Sehat | KB: Aturan pakai Herba Lambung Sehat | Produk: Herba Lambung Sehat",
        )
        ai_message_one.knowledge_entries.set(
            [
                seeded_entries["Manfaat Herba Lambung Sehat"],
                seeded_entries["Aturan pakai Herba Lambung Sehat"],
                seeded_entries["Kapan konsultasi medis diperlukan"],
            ]
        )

        session_two = ConsultationSession.objects.create(
            user=customer_user,
            title="Menjaga daya tahan tubuh",
            status=ConsultationSession.Status.CLOSED,
        )
        ConsultationMessage.objects.create(
            session=session_two,
            product=seeded_products["Herba Imuno Plus"],
            sender=ConsultationMessage.Sender.USER,
            content="Saya ingin produk herbal untuk bantu jaga imun saat kerja lembur.",
        )
        ai_message_two = ConsultationMessage.objects.create(
            session=session_two,
            product=seeded_products["Herba Imuno Plus"],
            sender=ConsultationMessage.Sender.AI,
            content="Untuk kebutuhan menjaga daya tahan tubuh saat aktivitas padat, Herba Imuno Plus atau Herba Fit Sehari dapat dipertimbangkan karena keduanya ditujukan untuk membantu kebugaran dan stamina harian. Gunakan sesuai anjuran kemasan, dan bila Anda memiliki riwayat alergi atau sedang menggunakan obat rutin, sebaiknya konsultasikan lebih dahulu.",
            confidence_score=0.84,
            used_rag=True,
            response_state=ConsultationMessage.ResponseState.ANSWERED,
            source_summary="KB: Manfaat Herba Imuno Plus | KB: Kapan produk herbal sebaiknya dikonsumsi | Produk: Herba Fit Sehari | Produk: Herba Imuno Plus",
        )
        ai_message_two.knowledge_entries.set(
            [
                seeded_entries["Manfaat Herba Imuno Plus"],
                seeded_entries["Kapan produk herbal sebaiknya dikonsumsi"],
                seeded_entries["Kehati-hatian penggunaan produk herbal"],
            ]
        )

        session_three = ConsultationSession.objects.create(
            user=customer_user,
            title="Apakah aman untuk ibu hamil",
            status=ConsultationSession.Status.CLOSED,
        )
        ConsultationMessage.objects.create(
            session=session_three,
            sender=ConsultationMessage.Sender.USER,
            content="Produk mana yang aman untuk ibu hamil muda yang sedang mual dan masuk angin?",
        )
        ConsultationMessage.objects.create(
            session=session_three,
            sender=ConsultationMessage.Sender.AI,
            content="Maaf, saya belum menemukan informasi yang cukup di knowledge base untuk menjawab pertanyaan ini. Pertanyaan Anda sudah disimpan agar dapat ditinjau lebih lanjut oleh AI Trainer.",
            confidence_score=0,
            used_rag=True,
            response_state=ConsultationMessage.ResponseState.FALLBACK,
            source_summary="KB: Kehati-hatian penggunaan produk herbal | KB: Batas sistem konsultasi herbal",
        )
        UnansweredQuestion.objects.update_or_create(
            session=session_three,
            customer=customer_user,
            question="Produk mana yang aman untuk ibu hamil muda yang sedang mual dan masuk angin?",
            defaults={
                "reason": "Sistem tidak menemukan konteks yang relevan di knowledge base.",
                "status": UnansweredQuestion.Status.OPEN,
            },
        )

        session_four = ConsultationSession.objects.create(
            user=customer_user,
            title="Interaksi dengan obat rutin",
            status=ConsultationSession.Status.ACTIVE,
        )
        ConsultationMessage.objects.create(
            session=session_four,
            product=seeded_products["Herba Stamina Prima"],
            sender=ConsultationMessage.Sender.USER,
            content="Saya minum obat tekanan darah tiap hari, apakah boleh minum herbal stamina?",
        )
        ai_message_four = ConsultationMessage.objects.create(
            session=session_four,
            product=seeded_products["Herba Stamina Prima"],
            sender=ConsultationMessage.Sender.AI,
            content="Penggunaan produk herbal bersama obat rutin membutuhkan kehati-hatian. Berdasarkan knowledge base, pengguna obat rutin sebaiknya berkonsultasi lebih dahulu untuk menilai kecocokan dan mengurangi risiko interaksi yang tidak diinginkan. Karena pertanyaan Anda berkaitan dengan obat tekanan darah, saya sarankan meminta arahan tenaga kesehatan sebelum menggunakan produk herbal stamina.",
            confidence_score=0.68,
            used_rag=True,
            response_state=ConsultationMessage.ResponseState.ANSWERED,
            source_summary="KB: Apakah produk herbal bisa diminum bersamaan dengan obat rutin | KB: Kehati-hatian penggunaan produk herbal | Produk: Herba Stamina Prima",
        )
        ai_message_four.knowledge_entries.set(
            [
                seeded_entries["Apakah produk herbal bisa diminum bersamaan dengan obat rutin"],
                seeded_entries["Kehati-hatian penggunaan produk herbal"],
                seeded_entries["Kapan konsultasi medis diperlukan"],
            ]
        )

        AIResponseReview.objects.filter(reviewer=trainer_user).delete()
        AIResponseReview.objects.create(
            message=ai_message_one,
            reviewer=trainer_user,
            verdict=AIResponseReview.Verdict.ACCURATE,
            note="Jawaban sudah sesuai konteks produk dan tetap memberi batasan medis.",
        )
        AIResponseReview.objects.create(
            message=ai_message_two,
            reviewer=trainer_user,
            verdict=AIResponseReview.Verdict.ACCURATE,
            note="Rekomendasi sudah relevan dengan tujuan menjaga daya tahan tubuh.",
        )
        AIResponseReview.objects.create(
            message=ai_message_four,
            reviewer=trainer_user,
            verdict=AIResponseReview.Verdict.NEEDS_REVISION,
            note="Sudah aman, tetapi ke depan bisa ditambah penjelasan produk stamina yang lebih spesifik.",
        )

        self.stdout.write(self.style.SUCCESS("Seed MVP selesai dijalankan."))
